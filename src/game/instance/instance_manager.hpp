/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_id.hpp"
#include "game/instance/instance_region_pool.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <cstdint>
	#include <functional>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <unordered_map>
	#include <vector>
#endif

enum class InstanceState : uint8_t {
	Creating,
	Active,
	Closing,
	Destroyed,
};

struct InstanceDefinition {
	std::string name;
	// 0 means no automatic timeout; the instance only closes when close()
	// is called explicitly.
	std::chrono::seconds timeout { 0 };
};

using InstanceCleanupCallback = std::function<void(InstanceId, const InstanceMapRegion &)>;

// Owns the configured map-region pool and the lifecycle of instances that
// reserve those regions. Deliberately a plain, constructor-instantiated class
// rather than a g_x() singleton.
class InstanceManager {
public:
	// Takes ownership of the complete configured region set. Construction
	// validates the regions through InstanceRegionPool before any instance can
	// be created.
	explicit InstanceManager(std::vector<InstanceMapRegion> regions);

	// non-copyable: owns unique region reservations and per-instance state.
	InstanceManager(const InstanceManager &) = delete;
	InstanceManager &operator=(const InstanceManager &) = delete;

	struct CreateResult {
		bool ok = false;
		InstanceId id = InstanceId::Invalid;
		std::string error;
	};

	// Reserves a free configured region and creates the instance in the
	// Creating state. Fails if every region is already reserved.
	[[nodiscard]] CreateResult createInstance(const InstanceDefinition &definition);

	// Creating -> Active. Returns false without changing anything if the
	// instance is unknown or not currently Creating.
	bool activate(InstanceId id);

	// Idempotent: {Creating, Active} -> Closing -> Destroyed. The cleanup
	// callback runs outside the manager lock exactly once and receives the
	// concrete reserved region. The region is returned to the pool only after
	// cleanup completes. If cleanup throws, the instance remains Closing and
	// the region stays quarantined instead of being exposed for reuse.
	bool close(InstanceId id);

	// Replaces the cleanup callback for an instance. No-op if the instance is
	// unknown. Safe to call before or after activate().
	void setCleanupCallback(InstanceId id, InstanceCleanupCallback callback);

	[[nodiscard]] std::optional<InstanceState> getState(InstanceId id) const;
	[[nodiscard]] std::optional<InstanceSlotId> getSlot(InstanceId id) const;
	[[nodiscard]] std::optional<InstanceMapRegion> getRegion(InstanceId id) const;

	// Closes every instance whose definition timeout has elapsed as of `now`.
	// Instances with timeout == 0 are never touched. Goes through the same
	// idempotent close() path.
	std::size_t closeExpiredInstances(std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now());

	[[nodiscard]] std::size_t activeInstanceCount() const;
	[[nodiscard]] std::size_t availableSlotCount() const;
	[[nodiscard]] std::size_t totalSlotCount() const;

private:
	struct InstanceRecord {
		InstanceId id = InstanceId::Invalid;
		InstanceMapRegion region;
		InstanceState state = InstanceState::Creating;
		InstanceDefinition definition;
		std::chrono::steady_clock::time_point expiresAt {};
		InstanceCleanupCallback cleanupCallback;
	};

	mutable std::mutex mutex;
	InstanceRegionPool regionPool;
	std::unordered_map<InstanceId, InstanceRecord> instances;
	uint32_t nextInstanceId = 1;
};
