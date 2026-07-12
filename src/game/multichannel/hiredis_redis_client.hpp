/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifdef CANARY_MULTICHANNEL_REDIS

	#include "game/multichannel/redis_client.hpp"

	#ifndef USE_PRECOMPILED_HEADERS
		#include <mutex>
		#include <string>
		#include <vector>
	#endif

struct redisContext;

class HiredisRedisClient final : public IRedisClient {
public:
	struct Options {
		std::string host = "127.0.0.1";
		int port = 6379;
		int database = 0;
		std::string username;
		std::string password;
		int connectTimeoutMs = 2000;
	};

	explicit HiredisRedisClient(Options options);
	~HiredisRedisClient() override;

	HiredisRedisClient(const HiredisRedisClient &) = delete;
	HiredisRedisClient &operator=(const HiredisRedisClient &) = delete;

	LeaseAcquireOutcome acquireLease(const std::string &lockKey, const std::string &sessionId, const std::string &channelId, const std::string &instanceId, int64_t ttlMs, int64_t nowMs) override;
	LeaseRenewOutcome renewLease(const std::string &lockKey, const std::string &sessionId, int64_t ttlMs, int64_t nowMs) override;
	bool releaseLease(const std::string &lockKey, const std::string &sessionId) override;
	std::optional<uint64_t> peekFencingToken(const std::string &lockKey) override;
	bool writeChannelRuntimeStatus(const std::string &runtimeKey, const ChannelRuntimeStatus &status, int64_t ttlMs, int64_t nowMs) override;
	std::optional<ChannelRuntimeStatus> readChannelRuntimeStatus(const std::string &runtimeKey, int64_t nowMs) override;

	[[nodiscard]] bool isHealthy() const override;

private:
	bool ensureConnected();
	std::vector<std::string> evalScript(std::string &cachedSha, const char* scriptBody, const std::string &key, const std::vector<std::string> &argv);

	Options options;
	redisContext* context = nullptr;
	mutable std::mutex mutex;
	bool healthy = false;

	std::string acquireSha;
	std::string renewSha;
	std::string releaseSha;
	std::string channelHeartbeatSha;
};

#endif // CANARY_MULTICHANNEL_REDIS
