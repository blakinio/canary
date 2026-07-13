/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_creature_binder.hpp"
#include "game/instance/instance_manager.hpp"
#include "game/movement/position.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstddef>
	#include <cstdint>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <unordered_map>
	#include <vector>
#endif

// The Instanced Test Arena's real consumer of InstanceManager (see
// docs/architecture/instanced-test-arena.md for the full region-selection
// evidence). Deliberately not a generic dungeon/instance framework: the
// region list is fixed and specific to this one administrator-only vertical
// slice.
//
// Takes the shared InstanceManager by reference (Game::getInstanceManager())
// rather than owning a second one - this program must not create an
// alternative manager, registry or binder.
class InstanceArenaService {
public:
	explicit InstanceArenaService(InstanceManager &manager) :
		manager(manager), binder(manager) { }

	InstanceArenaService(const InstanceArenaService &) = delete;
	InstanceArenaService &operator=(const InstanceArenaService &) = delete;

	// The two same-size, non-overlapping, evidence-backed regions this
	// feature is configured with. This is the single place the exact
	// coordinates from docs/architecture/instanced-test-arena.md are
	// written down; Game's InstanceManager member is constructed from this
	// list so there is exactly one region configuration in the codebase.
	[[nodiscard]] static std::vector<InstanceMapRegion> configuredRegions();

	struct CreateResult {
		bool ok = false;
		InstanceId id = InstanceId::Invalid;
		std::string error;
	};

	// Reserves a free arena region, creates the instance and activates it
	// immediately - the arena has no multi-step Creating setup phase.
	// Fails without creating a record when both regions are already
	// reserved.
	[[nodiscard]] CreateResult createArena();

	// Idempotent; delegates directly to InstanceManager::close().
	bool closeArena(InstanceId id);

	[[nodiscard]] std::optional<InstanceState> getState(InstanceId id) const;
	[[nodiscard]] std::optional<InstanceMapRegion> getRegion(InstanceId id) const;

	[[nodiscard]] InstanceManager &getManager() noexcept {
		return manager;
	}

	[[nodiscard]] InstanceCreatureBinder &getBinder() noexcept {
		return binder;
	}

	[[nodiscard]] std::size_t activeArenaCount() const;

	struct EnterResult {
		bool ok = false;
		Position entryPosition;
		std::string error;
	};

	// One stable player id owns at most one active arena session at a time.
	// Fails if playerId already has one (close it first) or if no region is
	// free. Remembers returnPosition for the later leaveArena()/
	// closeArenaForPlayer() call - it is never used to look the player up,
	// only to know where to send them back.
	[[nodiscard]] EnterResult enterArena(uint32_t playerId, const Position &returnPosition);

	struct LeaveResult {
		bool ok = false;
		Position returnPosition;
		std::string error;
	};

	// Fails if playerId has no active session. Returns the saved return
	// position without releasing the instance or its region - the arena
	// stays reserved until closeArenaForPlayer() (or a future timeout).
	[[nodiscard]] LeaveResult leaveArena(uint32_t playerId);

	struct CloseResult {
		bool ok = false;
		Position evacuationPosition;
		std::string error;
	};

	// Fails if playerId has no active session. Closes the underlying
	// instance and forgets the session; evacuationPosition is always the
	// saved return position, whether or not the player had already called
	// leaveArena() first.
	[[nodiscard]] CloseResult closeArenaForPlayer(uint32_t playerId);

	[[nodiscard]] bool hasActiveSession(uint32_t playerId) const;

private:
	struct PlayerSession {
		InstanceId instanceId = InstanceId::Invalid;
		Position returnPosition;
	};

	InstanceManager &manager;
	InstanceCreatureBinder binder;

	mutable std::mutex sessionMutex;
	std::unordered_map<uint32_t, PlayerSession> sessions;
};
