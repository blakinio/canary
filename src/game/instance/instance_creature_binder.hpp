/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_manager.hpp"

// Synchronous adapter between runtime objects exposing getID() and the
// pointer-free ownership registry. It keeps only the manager reference and
// never retains a Creature pointer/reference after a call returns.
class InstanceCreatureBinder {
public:
	explicit InstanceCreatureBinder(InstanceManager &manager) noexcept :
		manager(manager) {
	}

	InstanceCreatureBinder(const InstanceCreatureBinder &) = delete;
	InstanceCreatureBinder &operator=(const InstanceCreatureBinder &) = delete;

	bool bind(InstanceId instanceId, InstanceCreatureId creatureId) {
		return manager.registerCreature(instanceId, creatureId);
	}

	template <typename RuntimeCreature>
	bool bind(InstanceId instanceId, const RuntimeCreature &creature) {
		return bind(instanceId, static_cast<InstanceCreatureId>(creature.getID()));
	}

	// Uses the manager's authoritative reverse index rather than accepting a
	// caller-provided owner, so an object cannot accidentally unregister
	// another instance's creature.
	bool unbind(InstanceCreatureId creatureId) {
		const auto owner = manager.getCreatureOwner(creatureId);
		return owner && manager.unregisterCreature(*owner, creatureId);
	}

	template <typename RuntimeCreature>
	bool unbind(const RuntimeCreature &creature) {
		return unbind(static_cast<InstanceCreatureId>(creature.getID()));
	}

	bool inherit(InstanceCreatureId masterId, InstanceCreatureId summonId) {
		return manager.inheritCreatureOwnership(masterId, summonId);
	}

	template <typename RuntimeCreature>
	bool inherit(const RuntimeCreature &master, const RuntimeCreature &summon) {
		return inherit(
			static_cast<InstanceCreatureId>(master.getID()),
			static_cast<InstanceCreatureId>(summon.getID())
		);
	}

	[[nodiscard]] InstanceCreatureRelation relation(InstanceCreatureId firstId, InstanceCreatureId secondId) const {
		return manager.getCreatureRelation(firstId, secondId);
	}

	template <typename RuntimeCreature>
	[[nodiscard]] InstanceCreatureRelation relation(const RuntimeCreature &first, const RuntimeCreature &second) const {
		return relation(
			static_cast<InstanceCreatureId>(first.getID()),
			static_cast<InstanceCreatureId>(second.getID())
		);
	}

	[[nodiscard]] bool canInteract(InstanceCreatureId firstId, InstanceCreatureId secondId) const {
		return manager.canCreaturesInteract(firstId, secondId);
	}

	template <typename RuntimeCreature>
	[[nodiscard]] bool canInteract(const RuntimeCreature &first, const RuntimeCreature &second) const {
		return canInteract(
			static_cast<InstanceCreatureId>(first.getID()),
			static_cast<InstanceCreatureId>(second.getID())
		);
	}

	[[nodiscard]] std::optional<InstanceId> ownerOf(InstanceCreatureId creatureId) const {
		return manager.getCreatureOwner(creatureId);
	}

	template <typename RuntimeCreature>
	[[nodiscard]] std::optional<InstanceId> ownerOf(const RuntimeCreature &creature) const {
		return ownerOf(static_cast<InstanceCreatureId>(creature.getID()));
	}

private:
	InstanceManager &manager;
};
