/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
	#include <string>
	#include <vector>
#endif

// Read-only GM/admin lookups (docs/multichannel/OPERATIONS.md "GM / admin
// commands") against the `cluster_sessions` DB defense-in-depth layer
// (ARCHITECTURE.md §5) - not Redis, since a GM issuing these commands may
// well be on a different channel process than the target player(s), and the
// DB table is the one source both processes can always read regardless of
// which one is actually involved.
namespace multichannel {
	// Returns the channel_id currently recorded as ONLINE for playerId, or
	// std::nullopt if no such row exists (not currently online anywhere in
	// the cluster, as far as the DB mirror is concerned).
	[[nodiscard]] std::optional<int32_t> findOnlineChannelForPlayer(int32_t playerId);

	struct ClusterOnlinePlayerEntry {
		int32_t accountId = 0;
		int32_t playerId = 0;
		std::string playerName;
		int32_t channelId = 0;
	};

	// "Cluster-wide online list" (OPERATIONS.md): every player currently
	// recorded as ONLINE anywhere in the cluster, ordered by channel then
	// name.
	[[nodiscard]] std::vector<ClusterOnlinePlayerEntry> listOnlinePlayers();

	struct ClusterSessionLockInfo {
		int32_t accountId = 0;
		int32_t playerId = 0;
		int32_t channelId = 0;
		std::string instanceId;
		std::string sessionId;
		uint64_t fencingToken = 0;
		std::string status;
		int64_t acquiredAtMs = 0;
		int64_t lastHeartbeatMs = 0;
		int64_t expiresAtMs = 0;
	};

	// "Inspect a session's current lock owner and fencing token"
	// (OPERATIONS.md): the raw `cluster_sessions` row for playerId, whatever
	// its status - unlike findOnlineChannelForPlayer this is not filtered to
	// ONLINE, since inspecting a stale/DIRTY session is the primary reason a
	// GM would call this. Returns std::nullopt if no row has ever been
	// written for this player (lease never acquired).
	[[nodiscard]] std::optional<ClusterSessionLockInfo> findSessionLockInfo(int32_t playerId);
} // namespace multichannel
