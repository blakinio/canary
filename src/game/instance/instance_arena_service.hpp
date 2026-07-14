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
	#include <chrono>
	#include <cstddef>
	#include <cstdint>
	#include <functional>
	#include <memory>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <unordered_map>
	#include <vector>
#endif

class Monster;

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
	// Builds and places the arena's real monster at the given position,
	// returning null on failure. Defaults to a real Monster::createMonster()
	// + Game::placeCreature() factory (defined in the .cpp, so this header
	// never needs to include game.hpp/monster.hpp); tests inject a
	// synthetic factory instead, since Monster::createMonster()'s type
	// lookup and Game::placeCreature()'s map/tile access both need a fully
	// bootstrapped server that this repository's unit-test harness doesn't
	// provide (same constraint as Game itself - see docs/architecture/
	// instanced-test-arena.md).
	using MonsterFactory = std::function<std::shared_ptr<Monster>(const Position &position)>;

	// Removes one previously-spawned creature by its stable runtime id, as
	// part of arena cleanup. Defaults to Game::getCreatureByID() +
	// Game::removeCreature(), which also fires the existing automatic
	// unregister-on-removal hook (Game::removeCreature()); tests inject a
	// synthetic remover for the same reason as MonsterFactory above.
	using CreatureRemover = std::function<void(uint32_t creatureId)>;

	// Schedules callback to run once, delayMs from now. Defaults to
	// Game's dispatcher (g_dispatcher().scheduleEvent(...)); tests inject a
	// synthetic scheduler that records the callback instead of running it on
	// a real dispatcher, so the closing-warning behavior below can be driven
	// deterministically.
	using DelayedEventScheduler = std::function<void(uint32_t delayMs, std::function<void()> callback)>;

	// Sends playerId a text message if they are still online. Defaults to
	// Game::getPlayerByID() + Player::sendTextMessage(); tests inject a
	// synthetic notifier for the same reason as MonsterFactory above.
	using MessageNotifier = std::function<void(uint32_t playerId, const std::string &message)>;

	// Teleports playerId back to returnPosition if they are still online.
	// Defaults to Game::getPlayerByID() + Game::internalTeleport(), the same
	// mechanism Creature:teleportTo() uses in Lua; tests inject a synthetic
	// evacuator for the same reason as MonsterFactory above.
	using PlayerEvacuator = std::function<void(uint32_t playerId, const Position &returnPosition)>;

	explicit InstanceArenaService(InstanceManager &manager);
	InstanceArenaService(
		InstanceManager &manager,
		MonsterFactory monsterFactory,
		CreatureRemover creatureRemover,
		DelayedEventScheduler eventScheduler,
		MessageNotifier messageNotifier,
		PlayerEvacuator playerEvacuator
	);

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
		uint32_t monsterId = 0;
		std::string error;
	};

	// The monster spawned in every arena instance (docs/architecture/
	// instanced-test-arena.md): a plain, harmless, no-summon test monster
	// from the same datapack the region coordinates were verified against.
	static constexpr const char* MonsterName = "Cave Rat";

	// An idle arena (nobody ever called close) closes itself automatically
	// through the existing InstanceManager::closeExpiredInstances() sweep
	// (Game::start() already calls it periodically - docs/architecture/
	// instance-manager.md). A one-shot warning is scheduled this long before
	// that happens; see enterArena().
	static constexpr std::chrono::seconds ArenaTimeout { 15 * 60 };
	static constexpr std::chrono::seconds ArenaClosingWarningLeadTime { 2 * 60 };
	static_assert(ArenaClosingWarningLeadTime < ArenaTimeout, "the closing warning must fire before the arena times out");

	// One stable player id owns at most one active arena session at a time.
	// Fails if playerId already has one (close it first) or if no region is
	// free. Remembers returnPosition for the later leaveArena()/
	// closeArenaForPlayer() call - it is never used to look the player up,
	// only to know where to send them back. Also spawns and registers one
	// real monster in the reserved region; if the monster cannot be
	// created or placed, the whole arena is rolled back (instance closed)
	// and this fails - a session is never created without its monster.
	//
	// Also schedules a one-shot closing warning ArenaClosingWarningLeadTime
	// before ArenaTimeout elapses, guarded by an InstanceScopedEvent: if the
	// arena is no longer Active by the time the scheduler runs the callback
	// (closed manually, or already reaped), the callback is a no-op and no
	// message is sent - it never fires against a player who already left.
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

	// Fails if playerId has no active session. Removes the arena's monster
	// (and any summons it made) before closing the underlying instance -
	// InstanceManager::close() would otherwise quarantine an instance that
	// still has registered creatures - and forgets the session.
	// evacuationPosition is always the saved return position, whether or
	// not the player had already called leaveArena() first.
	[[nodiscard]] CloseResult closeArenaForPlayer(uint32_t playerId);

	[[nodiscard]] bool hasActiveSession(uint32_t playerId) const;

	// Evacuates and forgets any tracked session whose arena is no longer
	// Active (or has become unknown) - i.e. it expired via
	// InstanceManager::closeExpiredInstances() rather than through
	// closeArenaForPlayer(). Intended to run right after that sweep on the
	// same periodic tick (Game::start()); does not itself close anything -
	// the sweep already did. A no-op for sessions still Active.
	void reapExpiredSessions();

private:
	struct PlayerSession {
		InstanceId instanceId = InstanceId::Invalid;
		Position returnPosition;
	};

	InstanceManager &manager;
	InstanceCreatureBinder binder;
	MonsterFactory monsterFactory;
	CreatureRemover creatureRemover;
	DelayedEventScheduler eventScheduler;
	MessageNotifier messageNotifier;
	PlayerEvacuator playerEvacuator;

	mutable std::mutex sessionMutex;
	std::unordered_map<uint32_t, PlayerSession> sessions;
};
