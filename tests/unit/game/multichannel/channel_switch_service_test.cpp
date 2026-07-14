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
#include "injection_fixture.hpp"

#include "../../../shared/game/multichannel/fake_redis_client.hpp"

#include <gtest/gtest.h>
#include <memory>

namespace {
	ChannelSwitchRequest baseRequest() {
		ChannelSwitchRequest request;
		request.accountId = 1;
		request.playerId = 1;
		request.sourceChannelId = 1;
		request.targetChannelId = 2;
		request.lastChannelSwitchAt = 0;
		request.nowMs = 100000;
		request.cooldownMs = 60000;
		request.hasActivePzLockOrCombat = false;
		request.isSkulled = false;
		request.isInParty = false;
		request.partyPolicy = ChannelSwitchPartyPolicy::Deny;
		request.pvpExitPolicy = PvpChannelExitPolicy::CombatOrSkull;
		request.targetIsNoPvp = true;
		request.hasActiveClusterSessionElsewhere = false;
		request.targetChannelEnabled = true;
		request.targetChannelOnline = true;
		request.targetChannelFull = false;
		return request;
	}
} // namespace

TEST(ChannelSwitchServiceTest, PolicyParsers) {
	EXPECT_EQ(ChannelSwitchPartyPolicy::Deny, parseChannelSwitchPartyPolicy("deny"));
	EXPECT_EQ(ChannelSwitchPartyPolicy::Leave, parseChannelSwitchPartyPolicy("leave"));
	EXPECT_FALSE(parseChannelSwitchPartyPolicy("invalid").has_value());

	EXPECT_EQ(PvpChannelExitPolicy::CombatOnly, parsePvpChannelExitPolicy("combat-only"));
	EXPECT_EQ(PvpChannelExitPolicy::CombatOrSkull, parsePvpChannelExitPolicy("combat-or-skull"));
	EXPECT_FALSE(parsePvpChannelExitPolicy("invalid").has_value());
}

TEST(ChannelSwitchServiceTest, HappyPathIsAllowed) {
	const auto decision = ChannelSwitchService::evaluate(baseRequest());
	EXPECT_TRUE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::None, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, SameChannelIsNotATrueSwitch) {
	auto request = baseRequest();
	request.targetChannelId = *request.sourceChannelId;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::SameChannel, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, FirstEverLoginHasNoSourceChannelAndIsNotBlockedBySameChannelCheck) {
	auto request = baseRequest();
	request.sourceChannelId.reset();
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_TRUE(decision.allowed);
}

TEST(ChannelSwitchServiceTest, CooldownBlocksRapidSwitch) {
	auto request = baseRequest();
	request.lastChannelSwitchAt = 99000;
	request.nowMs = 100000; // only 1000ms since last switch, cooldown is 60000ms
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::Cooldown, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, CooldownExpiredAllowsSwitch) {
	auto request = baseRequest();
	request.lastChannelSwitchAt = 0;
	request.nowMs = 100000;
	request.cooldownMs = 60000;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_TRUE(decision.allowed);
}

TEST(ChannelSwitchServiceTest, AlreadyOnlineElsewhereBlocksSwitch) {
	auto request = baseRequest();
	request.hasActiveClusterSessionElsewhere = true;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::AlreadyOnlineElsewhere, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, PzLockOrCombatAlwaysBlocksRegardlessOfOtherFactors) {
	auto request = baseRequest();
	request.hasActivePzLockOrCombat = true;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::CombatOrPzLock, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, CombatOrSkullPolicyBlocksSkulledEntryToNoPvp) {
	auto request = baseRequest();
	request.pvpExitPolicy = PvpChannelExitPolicy::CombatOrSkull;
	request.isSkulled = true;
	request.targetIsNoPvp = true;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::SkullBlocksNoPvpEntry, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, CombatOnlyPolicyAllowsSkulledEntryToNoPvpWhenNotInCombat) {
	auto request = baseRequest();
	request.pvpExitPolicy = PvpChannelExitPolicy::CombatOnly;
	request.isSkulled = true;
	request.hasActivePzLockOrCombat = false;
	request.targetIsNoPvp = true;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_TRUE(decision.allowed);
}

TEST(ChannelSwitchServiceTest, SkullPolicyDoesNotApplyWhenTargetIsNotNoPvp) {
	auto request = baseRequest();
	request.pvpExitPolicy = PvpChannelExitPolicy::CombatOrSkull;
	request.isSkulled = true;
	request.targetIsNoPvp = false; // switching to another PvP channel
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_TRUE(decision.allowed);
}

TEST(ChannelSwitchServiceTest, PartyDenyPolicyBlocksSwitchOutright) {
	auto request = baseRequest();
	request.isInParty = true;
	request.partyPolicy = ChannelSwitchPartyPolicy::Deny;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::ActiveParty, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, PartyLeavePolicyAllowsSwitchButFlagsPartyLeave) {
	auto request = baseRequest();
	request.isInParty = true;
	request.partyPolicy = ChannelSwitchPartyPolicy::Leave;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_TRUE(decision.allowed);
	EXPECT_TRUE(decision.mustLeavePartyFirst);
}

TEST(ChannelSwitchServiceTest, NotInPartyNeverSetsMustLeaveFlag) {
	auto request = baseRequest();
	request.isInParty = false;
	request.partyPolicy = ChannelSwitchPartyPolicy::Leave;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_TRUE(decision.allowed);
	EXPECT_FALSE(decision.mustLeavePartyFirst);
}

TEST(ChannelSwitchServiceTest, DisabledTargetChannelIsRejected) {
	auto request = baseRequest();
	request.targetChannelEnabled = false;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::TargetDisabled, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, OfflineTargetChannelIsRejected) {
	auto request = baseRequest();
	request.targetChannelOnline = false;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::TargetOffline, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, FullTargetChannelIsRejected) {
	auto request = baseRequest();
	request.targetChannelFull = true;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::TargetFull, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, CombatCheckTakesPriorityOverPartyAndCapacityChecks) {
	// Even if every other reason to deny is also present, the reported
	// reason must be the combat/PZ lock check, since that one can never be
	// configured away and must never be shadowed by a "softer" reason.
	auto request = baseRequest();
	request.hasActivePzLockOrCombat = true;
	request.isInParty = true;
	request.partyPolicy = ChannelSwitchPartyPolicy::Deny;
	request.targetChannelFull = true;
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::CombatOrPzLock, decision.denyReason);
}

TEST(ChannelSwitchServiceTest, DescribeReturnsNonEmptyStringForEveryDenyReason) {
	const std::vector<ChannelSwitchDenyReason> allReasons = {
		ChannelSwitchDenyReason::None,
		ChannelSwitchDenyReason::SameChannel,
		ChannelSwitchDenyReason::Cooldown,
		ChannelSwitchDenyReason::AlreadyOnlineElsewhere,
		ChannelSwitchDenyReason::CombatOrPzLock,
		ChannelSwitchDenyReason::SkullBlocksNoPvpEntry,
		ChannelSwitchDenyReason::ActiveParty,
		ChannelSwitchDenyReason::TargetDisabled,
		ChannelSwitchDenyReason::TargetOffline,
		ChannelSwitchDenyReason::TargetFull,
	};
	for (const auto &reason : allReasons) {
		EXPECT_FALSE(describeChannelSwitchDenyReason(reason).empty());
	}
}

// --- Live target-channel availability (docs/multichannel/ARCHITECTURE.md
// §6): when ChannelRuntimeRegistry is enabled, evaluate() overrides the
// request's static targetChannelOnline/targetChannelFull fields with a live
// ChannelRuntimeRegistry::getAvailability() read, instead of trusting
// whatever the caller pre-populated (which may be stale by the time the
// switch is actually evaluated). Previously untested. ---

class ChannelSwitchServiceLiveAvailabilityTest : public ::testing::Test {
protected:
	void TearDown() override {
		g_channelRuntimeRegistry().resetForTesting();
	}

	InjectionFixture fixture_ {};
};

TEST_F(ChannelSwitchServiceLiveAvailabilityTest, LiveOnlineTargetOverridesStaleOfflineStaticFlag) {
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRuntimeRegistry().configure(fake, 1000);
	// No ChannelRegistry entry needed for channel 2 here - the live branch
	// only consults it for maxPlayers (defaults to 0, i.e. "no cap") when
	// absent; only the published heartbeat status matters for online/offline.

	const auto nowMs = multichannel::wallClockMs();
	ChannelRuntimeStatus status;
	status.channelId = 2;
	status.status = "ONLINE";
	status.lastHeartbeatMs = nowMs;
	ASSERT_TRUE(g_channelRuntimeRegistry().publishAndRefresh(status, 1000, { 2 }, nowMs));

	auto request = baseRequest();
	request.targetChannelOnline = false; // stale/wrong static flag
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_TRUE(decision.allowed);
}

TEST_F(ChannelSwitchServiceLiveAvailabilityTest, NoLiveHeartbeatOverridesStaleOnlineStaticFlag) {
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRuntimeRegistry().configure(fake, 1000);
	// Deliberately publish nothing for channel 2 - never reported in.

	auto request = baseRequest();
	request.targetChannelOnline = true; // stale/wrong static flag
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::TargetOffline, decision.denyReason);
}

TEST_F(ChannelSwitchServiceLiveAvailabilityTest, LiveFullTargetOverridesStaleNotFullStaticFlag) {
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRuntimeRegistry().configure(fake, 1000);
	ChannelInfo target;
	target.id = 2;
	target.maxPlayers = 5;
	g_channelRegistry().setChannelsForTesting({ target });

	const auto nowMs = multichannel::wallClockMs();
	ChannelRuntimeStatus status;
	status.channelId = 2;
	status.status = "ONLINE";
	status.playersOnline = 5;
	status.lastHeartbeatMs = nowMs;
	ASSERT_TRUE(g_channelRuntimeRegistry().publishAndRefresh(status, 1000, { 2 }, nowMs));

	auto request = baseRequest();
	request.targetChannelOnline = true;
	request.targetChannelFull = false; // stale/wrong static flag
	const auto decision = ChannelSwitchService::evaluate(request);
	EXPECT_FALSE(decision.allowed);
	EXPECT_EQ(ChannelSwitchDenyReason::TargetFull, decision.denyReason);
}
