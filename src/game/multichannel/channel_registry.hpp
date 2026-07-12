/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/channel_info.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <vector>
#endif

class ChannelRegistry {
public:
	ChannelRegistry() = default;
	ChannelRegistry(const ChannelRegistry &) = delete;
	ChannelRegistry &operator=(const ChannelRegistry &) = delete;

	static ChannelRegistry &getInstance();

	bool reload();
	[[nodiscard]] std::optional<ChannelInfo> getChannel(int32_t channelId) const;

	// Static/config eligibility only. Runtime heartbeat/capacity filtering is
	// performed by ChannelRuntimeRegistry.
	[[nodiscard]] std::vector<ChannelInfo> getLoginListChannels() const;
	[[nodiscard]] std::vector<ChannelInfo> getAllChannels() const;
	[[nodiscard]] std::size_t size() const;

	bool ensureBootstrapChannel();

	static std::string computeFileHash(const std::string &filePath);
	static std::string hashBytes(const unsigned char* data, std::size_t length);

	void setChannelsForTesting(std::vector<ChannelInfo> testChannels);

private:
	mutable std::mutex mutex;
	std::vector<ChannelInfo> channels;
};

constexpr auto g_channelRegistry = ChannelRegistry::getInstance;
