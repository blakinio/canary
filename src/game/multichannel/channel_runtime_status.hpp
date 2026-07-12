/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <string>
#endif

struct ChannelRuntimeStatus {
	int32_t channelId = 0;
	std::string instanceId;
	std::string nodeId;
	int64_t startedAtMs = 0;
	int64_t lastHeartbeatMs = 0;
	std::string status = "STARTING";
	int32_t playersOnline = 0;
	std::string buildSha;
	std::string mapHash;
	std::string dataHash;

	[[nodiscard]] bool hasValidState() const {
		return status == "STARTING" || status == "ONLINE" || status == "DRAINING" || status == "MAINTENANCE" || status == "OFFLINE";
	}

	[[nodiscard]] bool isFresh(int64_t nowMs, int64_t staleAfterMs) const {
		if (lastHeartbeatMs <= 0 || staleAfterMs <= 0 || nowMs < lastHeartbeatMs) {
			return false;
		}
		return nowMs - lastHeartbeatMs <= staleAfterMs;
	}

	[[nodiscard]] bool isOnline(int64_t nowMs, int64_t staleAfterMs) const {
		return hasValidState() && status == "ONLINE" && isFresh(nowMs, staleAfterMs);
	}
};
