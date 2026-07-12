/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#pragma once

#include "game/multichannel/channel_info.hpp"
#include "game/multichannel/channel_runtime_status.hpp"
#include "game/multichannel/redis_client.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <cstdint>
	#include <memory>
	#include <mutex>
	#include <optional>
	#include <unordered_map>
	#include <vector>
#endif

struct ChannelRuntimeAvailability {
	bool known = false;
	bool online = false;
	bool full = false;
	int32_t playersOnline = 0;
};

// Redis-backed fast path plus an in-process, fail-closed snapshot used by
// login and channel-switch call sites. Network I/O happens only in
// publishAndRefresh(); readers never perform Redis or DB work.
class ChannelRuntimeRegistry {
public:
	static ChannelRuntimeRegistry &getInstance() {
		static ChannelRuntimeRegistry instance;
		return instance;
	}

	ChannelRuntimeRegistry(const ChannelRuntimeRegistry &) = delete;
	ChannelRuntimeRegistry &operator=(const ChannelRuntimeRegistry &) = delete;

	void configure(std::shared_ptr<IRedisClient> client, int64_t newStaleAfterMs) {
		std::lock_guard lock(mutex);
		redisClient = std::move(client);
		staleAfterMs = newStaleAfterMs;
		statuses.clear();
		enabled = redisClient != nullptr && staleAfterMs > 0;
	}

	void resetForTesting() {
		std::lock_guard lock(mutex);
		redisClient.reset();
		statuses.clear();
		staleAfterMs = 0;
		enabled = false;
	}

	[[nodiscard]] bool isEnabled() const {
		std::lock_guard lock(mutex);
		return enabled;
	}

	// Intended to run from the existing multichannel heartbeat worker/cycle.
	// Any Redis connectivity failure clears the snapshot immediately so login
	// and switch fail closed instead of serving stale optimistic data.
	bool publishAndRefresh(const ChannelRuntimeStatus &ownStatus, int64_t ttlMs, const std::vector<int32_t> &channelIds, int64_t nowMs) {
		std::shared_ptr<IRedisClient> client;
		{
			std::lock_guard lock(mutex);
			if (!enabled || !redisClient) {
				return false;
			}
			client = redisClient;
		}

		if (!client->writeChannelRuntimeStatus(runtimeKey(ownStatus.channelId), ownStatus, ttlMs, nowMs)) {
			clearStatuses();
			return false;
		}

		std::unordered_map<int32_t, ChannelRuntimeStatus> refreshed;
		for (const auto channelId : channelIds) {
			const auto status = client->readChannelRuntimeStatus(runtimeKey(channelId), nowMs);
			if (!client->isHealthy()) {
				clearStatuses();
				return false;
			}
			if (status.has_value() && status->channelId == channelId && status->hasValidState()) {
				refreshed.emplace(channelId, *status);
			}
		}

		std::lock_guard lock(mutex);
		statuses = std::move(refreshed);
		return true;
	}

	[[nodiscard]] std::optional<ChannelRuntimeStatus> getStatus(int32_t channelId, int64_t nowMs) const {
		std::lock_guard lock(mutex);
		if (!enabled) {
			return std::nullopt;
		}
		const auto it = statuses.find(channelId);
		if (it == statuses.end() || !it->second.isFresh(nowMs, staleAfterMs)) {
			return std::nullopt;
		}
		return it->second;
	}

	[[nodiscard]] ChannelRuntimeAvailability getAvailability(int32_t channelId, int32_t maxPlayers, int64_t nowMs) const {
		ChannelRuntimeAvailability availability;
		const auto status = getStatus(channelId, nowMs);
		if (!status.has_value()) {
			return availability;
		}

		availability.known = true;
		availability.playersOnline = std::max<int32_t>(0, status->playersOnline);
		availability.online = status->status == "ONLINE";
		availability.full = availability.online && maxPlayers > 0 && availability.playersOnline >= maxPlayers;
		return availability;
	}

	[[nodiscard]] std::vector<ChannelInfo> getLoginListChannels(const std::vector<ChannelInfo> &channels, int64_t nowMs) const {
		std::vector<ChannelInfo> available;
		available.reserve(channels.size());
		for (const auto &channel : channels) {
			if (!channel.isSelectable()) {
				continue;
			}
			const auto runtime = getAvailability(channel.id, channel.maxPlayers, nowMs);
			if (runtime.online && !runtime.full) {
				available.push_back(channel);
			}
		}
		std::sort(available.begin(), available.end(), [](const ChannelInfo &a, const ChannelInfo &b) {
			if (a.sortOrder != b.sortOrder) {
				return a.sortOrder < b.sortOrder;
			}
			return a.id < b.id;
		});
		return available;
	}

	void setStatusesForTesting(int64_t newStaleAfterMs, std::vector<ChannelRuntimeStatus> testStatuses) {
		std::lock_guard lock(mutex);
		statuses.clear();
		for (auto &status : testStatuses) {
			statuses.emplace(status.channelId, std::move(status));
		}
		staleAfterMs = newStaleAfterMs;
		enabled = true;
	}

	[[nodiscard]] static std::string runtimeKey(int32_t channelId) {
		return "cluster:channel:" + std::to_string(channelId) + ":runtime";
	}

private:
	ChannelRuntimeRegistry() = default;

	void clearStatuses() {
		std::lock_guard lock(mutex);
		statuses.clear();
	}

	mutable std::mutex mutex;
	std::shared_ptr<IRedisClient> redisClient;
	std::unordered_map<int32_t, ChannelRuntimeStatus> statuses;
	int64_t staleAfterMs = 0;
	bool enabled = false;
};

constexpr auto g_channelRuntimeRegistry = ChannelRuntimeRegistry::getInstance;
