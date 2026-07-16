/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/cluster_record_ownership.hpp"

#include <map>
#include <mutex>
#include <utility>

// Test double for IClusterRecordOwnershipResolver: a caller-programmable
// map of (recordKind, recordId) -> ClusterRecordOwnership, defaulting to
// Unknown for anything not explicitly set - fail-closed by default,
// matching the production resolver's own fail-closed default (design doc
// §4.1/§14 tests 3, 4, 8, 12, 16).
class FakeClusterRecordOwnershipResolver : public IClusterRecordOwnershipResolver {
public:
	ClusterRecordOwnership resolve(const std::string &recordKind, int32_t recordId, const std::optional<int32_t> &recordChannelId) override {
		std::lock_guard lock(mutex);
		++resolveCallCount;

		// Statically-owned kinds echo the caller-supplied channel id
		// straight back, exactly like the real DbClusterRecordOwnershipResolver
		// does for HOUSE when recordChannelId is already known.
		if (recordChannelId.has_value()) {
			return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::OwnedByChannel, *recordChannelId };
		}

		const auto it = overrides.find({ recordKind, recordId });
		if (it == overrides.end()) {
			return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::Unknown, 0 };
		}
		return it->second;
	}

	void setOwnedByChannelForTesting(const std::string &recordKind, int32_t recordId, int32_t channelId) {
		std::lock_guard lock(mutex);
		overrides[{ recordKind, recordId }] = ClusterRecordOwnership { ClusterRecordOwnershipOutcome::OwnedByChannel, channelId };
	}

	void setNoLiveOwnerForTesting(const std::string &recordKind, int32_t recordId) {
		std::lock_guard lock(mutex);
		overrides[{ recordKind, recordId }] = ClusterRecordOwnership { ClusterRecordOwnershipOutcome::NoLiveOwner, 0 };
	}

	void setUnknownForTesting(const std::string &recordKind, int32_t recordId) {
		std::lock_guard lock(mutex);
		overrides[{ recordKind, recordId }] = ClusterRecordOwnership { ClusterRecordOwnershipOutcome::Unknown, 0 };
	}

	[[nodiscard]] int32_t resolveCallCountForTesting() const {
		std::lock_guard lock(mutex);
		return resolveCallCount;
	}

private:
	mutable std::mutex mutex;
	std::map<std::pair<std::string, int32_t>, ClusterRecordOwnership> overrides;
	int32_t resolveCallCount = 0;
};
