/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_config_validator.hpp"

#include "game/multichannel/channel_switch_service.hpp"

std::string describeClusterConfigValidationError(ClusterConfigValidationError error) {
	switch (error) {
		case ClusterConfigValidationError::LeaseTtlNotGreaterThanHeartbeat:
			return "sessionLeaseTtl must be strictly greater than sessionHeartbeatInterval";
		case ClusterConfigValidationError::InvalidPartyPolicy:
			return "channelSwitchPartyPolicy must be 'deny' or 'leave'";
		case ClusterConfigValidationError::InvalidPvpExitPolicy:
			return "pvpChannelExitPolicy must be 'combat-only' or 'combat-or-skull'";
		case ClusterConfigValidationError::RedisClientNotCompiledIn:
			return "multiChannelEnabled=true requires a build with the optional vcpkg 'multichannel' feature (Redis client); refusing to start without it";
		case ClusterConfigValidationError::CurrentChannelMissing:
			return "no `channels` row found for this process's resolved channel id";
		case ClusterConfigValidationError::CurrentChannelDisabled:
			return "this process's channel is disabled in the `channels` table";
		case ClusterConfigValidationError::CurrentChannelInvalidPvpType:
			return "this process's channel has an invalid pvp_type";
		case ClusterConfigValidationError::MultipleLoginGatewaysEnabled:
			return "more than one enabled channel has login_gateway=true; exactly one login gateway is allowed cluster-wide";
		case ClusterConfigValidationError::RedisTlsNotSupported:
			return "redisUseTls=true is not supported by this build's Redis client yet; refusing to silently connect without TLS";
		case ClusterConfigValidationError::RedisPingDnsFailure:
			return "live Redis PING failed: could not resolve the configured Redis host; check redisHost";
		case ClusterConfigValidationError::RedisPingConnectionRefused:
			return "live Redis PING failed: connection refused; check that Redis is running and redisHost/redisPort are correct";
		case ClusterConfigValidationError::RedisPingTimeout:
			return "live Redis PING failed: connection timed out; check network reachability and firewall rules to the configured Redis host";
		case ClusterConfigValidationError::RedisPingAuthenticationFailed:
			return "live Redis PING failed: authentication rejected; check redisUsername/redisPassword";
		case ClusterConfigValidationError::RedisPingUnexpectedResponse:
			return "live Redis PING failed: the server responded, but not with the expected PONG; check that redisHost/redisPort actually point at a Redis server";
		case ClusterConfigValidationError::RedisPingOtherFailure:
			return "live Redis PING failed for an unclassified reason; see the server log for the raw connection error";
	}
	return "unknown validation error";
}

namespace {
	std::optional<ClusterConfigValidationError> redisPingFailureError(RedisPingOutcome outcome) {
		switch (outcome) {
			case RedisPingOutcome::Success:
				return std::nullopt;
			case RedisPingOutcome::DnsFailure:
				return ClusterConfigValidationError::RedisPingDnsFailure;
			case RedisPingOutcome::ConnectionRefused:
				return ClusterConfigValidationError::RedisPingConnectionRefused;
			case RedisPingOutcome::Timeout:
				return ClusterConfigValidationError::RedisPingTimeout;
			case RedisPingOutcome::AuthenticationFailed:
				return ClusterConfigValidationError::RedisPingAuthenticationFailed;
			case RedisPingOutcome::UnexpectedResponse:
				return ClusterConfigValidationError::RedisPingUnexpectedResponse;
			case RedisPingOutcome::Other:
				return ClusterConfigValidationError::RedisPingOtherFailure;
		}
		return ClusterConfigValidationError::RedisPingOtherFailure;
	}
} // namespace

ClusterConfigValidationResult ClusterConfigValidator::validate(const ClusterConfigValidationInput &input) {
	ClusterConfigValidationResult result;

	if (!input.multiChannelEnabled) {
		// Single-channel mode: validation is a deliberate no-op (spec §13 -
		// existing installs must boot unchanged).
		return result;
	}

	if (input.sessionLeaseTtlMs <= input.sessionHeartbeatIntervalMs) {
		result.valid = false;
		result.errors.push_back(ClusterConfigValidationError::LeaseTtlNotGreaterThanHeartbeat);
	} else if (input.sessionLeaseTtlMs < input.sessionHeartbeatIntervalMs * 2) {
		result.warnings.push_back("sessionLeaseTtl is less than 2x sessionHeartbeatInterval; a single missed heartbeat can expire the lease. Consider increasing the margin.");
	}

	if (!parseChannelSwitchPartyPolicy(input.channelSwitchPartyPolicy).has_value()) {
		result.valid = false;
		result.errors.push_back(ClusterConfigValidationError::InvalidPartyPolicy);
	}

	if (!parsePvpChannelExitPolicy(input.pvpChannelExitPolicy).has_value()) {
		result.valid = false;
		result.errors.push_back(ClusterConfigValidationError::InvalidPvpExitPolicy);
	}

	if (!input.redisClientCompiledIn) {
		result.valid = false;
		result.errors.push_back(ClusterConfigValidationError::RedisClientNotCompiledIn);
	} else {
		// Only meaningful once a client actually exists to ping - when it
		// doesn't (redisClientCompiledIn == false), RedisClientNotCompiledIn
		// above already fails closed for the right reason; reporting a ping
		// failure too would be a confusing, redundant second error. A
		// nullopt outcome (ping never attempted) is treated the same as a
		// failure - see ClusterConfigValidationInput::redisPingOutcome.
		if (const auto pingError = redisPingFailureError(input.redisPingOutcome.value_or(RedisPingOutcome::Other))) {
			result.valid = false;
			result.errors.push_back(*pingError);
		}
	}

	if (input.redisUseTls) {
		result.valid = false;
		result.errors.push_back(ClusterConfigValidationError::RedisTlsNotSupported);
	}

	if (!input.currentChannel.has_value()) {
		result.valid = false;
		result.errors.push_back(ClusterConfigValidationError::CurrentChannelMissing);
	} else {
		if (!input.currentChannel->enabled) {
			result.valid = false;
			result.errors.push_back(ClusterConfigValidationError::CurrentChannelDisabled);
		}
		if (!input.currentChannel->isValidPvpType()) {
			result.valid = false;
			result.errors.push_back(ClusterConfigValidationError::CurrentChannelInvalidPvpType);
		}
	}

	if (input.enabledLoginGatewayCount > 1) {
		result.valid = false;
		result.errors.push_back(ClusterConfigValidationError::MultipleLoginGatewaysEnabled);
	}

	return result;
}
