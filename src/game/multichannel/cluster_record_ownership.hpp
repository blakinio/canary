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
#endif

// Record kinds this mechanism currently knows how to resolve ownership
// for. A string, not a closed set at the DB layer (see
// cluster_pending_operation_repository.hpp) - these constants are this
// module's own vocabulary, not a schema constraint.
namespace multichannel {
	inline constexpr const char* RecordKindPlayerInbox = "PLAYER_INBOX";
	inline constexpr const char* RecordKindHouse = "HOUSE";
} // namespace multichannel

// Tri-state outcome, deliberately not a bool+optional pair: "no live owner"
// and "cannot currently confirm" must never be conflated, since only the
// former is safe to treat as "apply directly" (design doc §4.11.2) - the
// latter must fail closed exactly like every other uncertain-Redis-state
// case in this codebase (design doc §4.7/§14 test 12).
enum class ClusterRecordOwnershipOutcome : uint8_t {
	OwnedByChannel, // ownerChannelId is valid
	NoLiveOwner, // confirmed: safe to apply directly, guarded per §4.11.2
	Unknown, // cannot currently confirm - caller must defer, not guess
};

struct ClusterRecordOwnership {
	ClusterRecordOwnershipOutcome outcome = ClusterRecordOwnershipOutcome::Unknown;
	int32_t ownerChannelId = 0; // valid only when outcome == OwnedByChannel
};

// Resolves "which channel currently owns this record, if any" in one
// atomic call - docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md §4.1.
// Deliberately does not persist or cache anything itself: every call
// re-resolves from the existing authoritative source for that record kind
// (cluster_sessions for PLAYER_INBOX, houses.channel_id for HOUSE) - there
// is no cached belief about ownership to go stale (design doc §4.12).
class IClusterRecordOwnershipResolver {
public:
	virtual ~IClusterRecordOwnershipResolver() = default;

	// recordChannelId is provided for statically-owned kinds (HOUSE) where
	// the "current owner" is just that value, echoed back as
	// OwnedByChannel - passing it avoids a second lookup when the caller
	// already knows it (e.g. from an already-loaded
	// ClusterPendingOperationRecord). Ignored for dynamically-owned kinds
	// (PLAYER_INBOX).
	[[nodiscard]] virtual ClusterRecordOwnership resolve(const std::string &recordKind, int32_t recordId, const std::optional<int32_t> &recordChannelId) = 0;
};
