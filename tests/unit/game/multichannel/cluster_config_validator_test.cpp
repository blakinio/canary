/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_config_validator.hpp"

#include <algorithm>
#include <gtest/gtest.h>

namespace {
	ClusterConfigValidationInput validInput() {
		ClusterConfigValidationInput input;
		input.multiChannelEnabled = true;
		input.sessionLeaseTtlMs = 30000;
		input.sessionHeartbeatIntervalMs = 5000;
		input.channelSwitchPartyPolicy = "deny";
		input.pvpChannelExitPolicy = "combat-or-skull";
		input.redisClientCompiledIn = true;
		input.enabledLoginGatewayCount = 1;
		input.redisPingOutcome = RedisPingOutcome::Success;

		ChannelInfo channel;
		channel.id = 1;
		channel.name = "Channel 1";
		channel.pvpType = "no-pvp";
		channel.enabled = true;
		input.currentChannel = channel;
		return input;
	}

	bool contains(const std::vector<ClusterConfigValidationError> &errors, ClusterConfigValidationError target) {
		return std::ranges::find(errors, target) != errors.end();
	}
} // namespace

TEST(ClusterConfigValidatorTest, SingleChannelModeIsAlwaysValidNoOp) {
	ClusterConfigValidationInput input;
	input.multiChannelEnabled = false;
	// Deliberately leave every other field at its invalid default - must
	// still be valid, since validation is a no-op when disabled.
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_TRUE(result.valid);
	EXPECT_TRUE(result.errors.empty());
}

TEST(ClusterConfigValidatorTest, ValidInputPasses) {
	const auto result = ClusterConfigValidator::validate(validInput());
	EXPECT_TRUE(result.valid);
	EXPECT_TRUE(result.errors.empty());
}

TEST(ClusterConfigValidatorTest, RejectsLeaseTtlNotGreaterThanHeartbeat) {
	auto input = validInput();
	input.sessionLeaseTtlMs = 5000;
	input.sessionHeartbeatIntervalMs = 5000;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::LeaseTtlNotGreaterThanHeartbeat));
}

TEST(ClusterConfigValidatorTest, WarnsButDoesNotFailWhenMarginIsThin) {
	auto input = validInput();
	input.sessionLeaseTtlMs = 6000;
	input.sessionHeartbeatIntervalMs = 5000; // > but < 2x
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_TRUE(result.valid);
	EXPECT_FALSE(result.warnings.empty());
}

TEST(ClusterConfigValidatorTest, RejectsInvalidPartyPolicy) {
	auto input = validInput();
	input.channelSwitchPartyPolicy = "not-a-policy";
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::InvalidPartyPolicy));
}

TEST(ClusterConfigValidatorTest, RejectsInvalidPvpExitPolicy) {
	auto input = validInput();
	input.pvpChannelExitPolicy = "not-a-policy";
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::InvalidPvpExitPolicy));
}

TEST(ClusterConfigValidatorTest, RejectsWhenRedisClientNotCompiledIn) {
	auto input = validInput();
	input.redisClientCompiledIn = false;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisClientNotCompiledIn));
}

TEST(ClusterConfigValidatorTest, RejectsWhenCurrentChannelIsMissing) {
	auto input = validInput();
	input.currentChannel.reset();
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::CurrentChannelMissing));
}

TEST(ClusterConfigValidatorTest, RejectsWhenCurrentChannelIsDisabled) {
	auto input = validInput();
	input.currentChannel->enabled = false;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::CurrentChannelDisabled));
}

TEST(ClusterConfigValidatorTest, RejectsWhenCurrentChannelHasInvalidPvpType) {
	auto input = validInput();
	input.currentChannel->pvpType = "free-for-all";
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::CurrentChannelInvalidPvpType));
}

TEST(ClusterConfigValidatorTest, RejectsRedisUseTls) {
	auto input = validInput();
	input.redisUseTls = true;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisTlsNotSupported));
}

TEST(ClusterConfigValidatorTest, AllowsExactlyOneEnabledLoginGateway) {
	auto input = validInput();
	input.enabledLoginGatewayCount = 1;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_TRUE(result.valid);
}

TEST(ClusterConfigValidatorTest, AllowsZeroEnabledLoginGateways) {
	// Not ideal operationally (nothing serves logins), but not this
	// validator's job to catch - it only rejects an unambiguous conflict.
	auto input = validInput();
	input.enabledLoginGatewayCount = 0;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_TRUE(result.valid);
}

TEST(ClusterConfigValidatorTest, RejectsMultipleEnabledLoginGateways) {
	auto input = validInput();
	input.enabledLoginGatewayCount = 2;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::MultipleLoginGatewaysEnabled));
}

// --- Live Redis PING (docs/multichannel/ARCHITECTURE.md §4.4): "Redis is
// configured" or "a client object was constructed" is not proof Redis is
// reachable - only a real round-trip is. redisPingOutcome is a plain input
// (the live I/O happens in the caller, before validate() runs) so this
// stays a pure, fully unit-testable function without touching a real Redis. ---

TEST(ClusterConfigValidatorTest, AcceptsSuccessfulPing) {
	auto input = validInput();
	input.redisPingOutcome = RedisPingOutcome::Success;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_TRUE(result.valid);
}

TEST(ClusterConfigValidatorTest, RejectsDnsFailure) {
	auto input = validInput();
	input.redisPingOutcome = RedisPingOutcome::DnsFailure;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisPingDnsFailure));
}

TEST(ClusterConfigValidatorTest, RejectsConnectionRefused) {
	auto input = validInput();
	input.redisPingOutcome = RedisPingOutcome::ConnectionRefused;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisPingConnectionRefused));
}

TEST(ClusterConfigValidatorTest, RejectsTimeout) {
	auto input = validInput();
	input.redisPingOutcome = RedisPingOutcome::Timeout;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisPingTimeout));
}

TEST(ClusterConfigValidatorTest, RejectsAuthenticationFailed) {
	auto input = validInput();
	input.redisPingOutcome = RedisPingOutcome::AuthenticationFailed;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisPingAuthenticationFailed));
}

TEST(ClusterConfigValidatorTest, RejectsUnexpectedResponse) {
	auto input = validInput();
	input.redisPingOutcome = RedisPingOutcome::UnexpectedResponse;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisPingUnexpectedResponse));
}

TEST(ClusterConfigValidatorTest, RejectsOtherPingFailure) {
	auto input = validInput();
	input.redisPingOutcome = RedisPingOutcome::Other;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisPingOtherFailure));
}

TEST(ClusterConfigValidatorTest, UnattemptedPingIsTreatedAsFailure) {
	// A caller that forgot to actually ping (nullopt) must not silently pass
	// as if it had succeeded - fail-closed default for "unknown" the same
	// as for "failed".
	auto input = validInput();
	input.redisPingOutcome.reset();
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisPingOtherFailure));
}

TEST(ClusterConfigValidatorTest, PingNotAttemptedIsIgnoredWhenRedisClientNotCompiledIn) {
	// There is nothing to ping when the client isn't even compiled in -
	// RedisClientNotCompiledIn alone must fail closed, without also
	// reporting a redundant, confusing ping-failure error for a ping that
	// could never have been attempted.
	auto input = validInput();
	input.redisClientCompiledIn = false;
	input.redisPingOutcome.reset();
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_TRUE(contains(result.errors, ClusterConfigValidationError::RedisClientNotCompiledIn));
	EXPECT_FALSE(contains(result.errors, ClusterConfigValidationError::RedisPingOtherFailure));
}

TEST(ClusterConfigValidatorTest, CollectsMultipleErrorsAtOnce) {
	auto input = validInput();
	input.channelSwitchPartyPolicy = "bad";
	input.pvpChannelExitPolicy = "bad";
	input.redisClientCompiledIn = false;
	const auto result = ClusterConfigValidator::validate(input);
	EXPECT_FALSE(result.valid);
	EXPECT_GE(result.errors.size(), 3u);
}

TEST(ClusterConfigValidatorTest, DescribeReturnsNonEmptyStringForEveryError) {
	const std::vector<ClusterConfigValidationError> allErrors = {
		ClusterConfigValidationError::LeaseTtlNotGreaterThanHeartbeat,
		ClusterConfigValidationError::InvalidPartyPolicy,
		ClusterConfigValidationError::InvalidPvpExitPolicy,
		ClusterConfigValidationError::RedisClientNotCompiledIn,
		ClusterConfigValidationError::CurrentChannelMissing,
		ClusterConfigValidationError::CurrentChannelDisabled,
		ClusterConfigValidationError::CurrentChannelInvalidPvpType,
		ClusterConfigValidationError::MultipleLoginGatewaysEnabled,
		ClusterConfigValidationError::RedisTlsNotSupported,
		ClusterConfigValidationError::RedisPingDnsFailure,
		ClusterConfigValidationError::RedisPingConnectionRefused,
		ClusterConfigValidationError::RedisPingTimeout,
		ClusterConfigValidationError::RedisPingAuthenticationFailed,
		ClusterConfigValidationError::RedisPingUnexpectedResponse,
		ClusterConfigValidationError::RedisPingOtherFailure,
	};
	for (const auto &error : allErrors) {
		EXPECT_FALSE(describeClusterConfigValidationError(error).empty());
	}
}
