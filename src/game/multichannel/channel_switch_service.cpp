/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/channel_switch_service.hpp"

#include "game/multichannel/channel_registry.hpp"
#include "game/multichannel/channel_runtime_registry.hpp"
#include "game/multichannel/wall_clock.hpp"

std::optional<ChannelSwitchPartyPolicy> parseChannelSwitchPartyPolicy(const std::string &value) {
	if (value == "deny") {
		return ChannelSwitchPartyPolicy::Deny;
	}
	if (value == "leave") {
		return ChannelSwitchPartyPolicy::Leave;
	}
	return std::nullopt;
}

std::optional<PvpChannelExitPolicy> parsePvpChannelExitPolicy(const std::string &value) {
	if (value == "combat-only") {
		return PvpChannelExitPolicy::CombatOnly;
	}
	if (value == "combat-or-skull") {
		return PvpChannelExitPolicy::CombatOrSkull;
	}
	return std::nullopt;
}

std::string describeChannelSwitchDenyReason(ChannelSwitchDenyReason reason) {
	switch (reason) {
		case ChannelSwitchDenyReason::None:
			return "No reason (switch was allowed).";
		case ChannelSwitchDenyReason::SameChannel:
			return "You are already on that channel.";
		case ChannelSwitchDenyReason::Cooldown:
			return "You must wait before switching channels again.";
		case ChannelSwitchDenyReason::AlreadyOnlineElsewhere:
			return "Your account is already online elsewhere.";
		case ChannelSwitchDenyReason::CombatOrPzLock:
			return "You cannot switch channels while in combat outside a protection zone.";
		case ChannelSwitchDenyReason::SkullBlocksNoPvpEntry:
			return "You cannot enter a non-PvP channel while skulled.";
		case ChannelSwitchDenyReason::ActiveParty:
			return "You cannot switch channels while in a party.";
		case ChannelSwitchDenyReason::TargetDisabled:
			return "That channel is currently disabled.";
		case ChannelSwitchDenyReason::TargetOffline:
			return "That channel is currently offline.";
		case ChannelSwitchDenyReason::TargetFull:
			return "That channel is currently full.";
	}
	return "Unknown reason.";
}

namespace {
	ChannelSwitchDecision deny(ChannelSwitchDenyReason reason) {
		ChannelSwitchDecision decision;
		decision.allowed = false;
		decision.denyReason = reason;
		return decision;
	}

} // namespace

ChannelSwitchDecision ChannelSwitchService::evaluate(const ChannelSwitchRequest &request) {
	if (request.sourceChannelId.has_value() && *request.sourceChannelId == request.targetChannelId) {
		return deny(ChannelSwitchDenyReason::SameChannel);
	}

	if (request.lastChannelSwitchAt > 0 && (request.nowMs - request.lastChannelSwitchAt) < request.cooldownMs) {
		return deny(ChannelSwitchDenyReason::Cooldown);
	}

	if (request.hasActiveClusterSessionElsewhere) {
		return deny(ChannelSwitchDenyReason::AlreadyOnlineElsewhere);
	}

	if (request.hasActivePzLockOrCombat) {
		return deny(ChannelSwitchDenyReason::CombatOrPzLock);
	}

	if (request.targetIsNoPvp && request.pvpExitPolicy == PvpChannelExitPolicy::CombatOrSkull && request.isSkulled) {
		return deny(ChannelSwitchDenyReason::SkullBlocksNoPvpEntry);
	}

	bool mustLeavePartyFirst = false;
	if (request.isInParty) {
		if (request.partyPolicy == ChannelSwitchPartyPolicy::Deny) {
			return deny(ChannelSwitchDenyReason::ActiveParty);
		}
		mustLeavePartyFirst = true;
	}

	if (!request.targetChannelEnabled) {
		return deny(ChannelSwitchDenyReason::TargetDisabled);
	}

	bool targetOnline = request.targetChannelOnline;
	bool targetFull = request.targetChannelFull;
	if (g_channelRuntimeRegistry().isEnabled()) {
		const auto targetChannel = g_channelRegistry().getChannel(request.targetChannelId);
		const int32_t maxPlayers = targetChannel.has_value() ? targetChannel->maxPlayers : 0;
		const auto availability = g_channelRuntimeRegistry().getAvailability(request.targetChannelId, maxPlayers, multichannel::wallClockMs());
		targetOnline = availability.online;
		targetFull = availability.full;
	}

	if (!targetOnline) {
		return deny(ChannelSwitchDenyReason::TargetOffline);
	}
	if (targetFull) {
		return deny(ChannelSwitchDenyReason::TargetFull);
	}

	ChannelSwitchDecision decision;
	decision.allowed = true;
	decision.denyReason = ChannelSwitchDenyReason::None;
	decision.mustLeavePartyFirst = mustLeavePartyFirst;
	return decision;
}
