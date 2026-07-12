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
#endif

// Read-only GM/admin lookup (docs/multichannel/OPERATIONS.md "GM / admin
// commands": "Locate a player's current channel") against the
// `cluster_sessions` DB defense-in-depth layer (ARCHITECTURE.md §5) - not
// Redis, since a GM issuing this command may well be on a different channel
// process than the target player, and the DB table is the one source both
// processes can always read regardless of which one the target is actually
// logged into.
namespace multichannel {
	// Returns the channel_id currently recorded as ONLINE for playerId, or
	// std::nullopt if no such row exists (not currently online anywhere in
	// the cluster, as far as the DB mirror is concerned).
	[[nodiscard]] std::optional<int32_t> findOnlineChannelForPlayer(int32_t playerId);
} // namespace multichannel
