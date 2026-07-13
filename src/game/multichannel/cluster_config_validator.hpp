/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/channel_info.hpp"
#include "game/multichannel/redis_client.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
	#include <string>
	#include <vector>
#endif

enum class ClusterConfigValidationError : uint8_t {
	LeaseTtlNotGreaterThanHeartbeat,
	InvalidPartyPolicy,
	InvalidPvpExitPolicy,
	RedisClientNotCompiledIn,
	CurrentChannelMissing,
	CurrentChannelDisabled,
	CurrentChannelInvalidPvpType,
	MultipleLoginGatewaysEnabled,
	RedisTlsNotSupported,
	// One value per RedisPingOutcome failure category (Success excluded) -
	// see ClusterConfigValidationInput::redisPingOutcome. Kept as distinct
	// values rather than one generic "ping failed" so
	// describeClusterConfigValidationError gives a specific, readable
	// startup error per category without needing extra caller-side state.
	RedisPingDnsFailure,
	RedisPingConnectionRefused,
	RedisPingTimeout,
	RedisPingAuthenticationFailed,
	RedisPingUnexpectedResponse,
	RedisPingOtherFailure,
};

[[nodiscard]] std::string describeClusterConfigValidationError(ClusterConfigValidationError error);

struct ClusterConfigValidationInput {
	bool multiChannelEnabled = false;
	int64_t sessionLeaseTtlMs = 0;
	int64_t sessionHeartbeatIntervalMs = 0;
	std::string channelSwitchPartyPolicy;
	std::string pvpChannelExitPolicy;
	// Whether this binary was compiled with the optional vcpkg
	// "multichannel" feature (CANARY_MULTICHANNEL_REDIS). See
	// docs/multichannel/ARCHITECTURE.md §9.
	bool redisClientCompiledIn = false;
	// The production HiredisRedisClient (src/game/multichannel/
	// hiredis_redis_client.*) only speaks plain TCP to Redis; it does not
	// link hiredis_ssl. redisUseTls=true would silently connect without TLS
	// if not caught here - fail closed instead (see ARCHITECTURE.md §9).
	bool redisUseTls = false;
	// The `channels` row for this process's resolved channel id, if the
	// registry has one.
	std::optional<ChannelInfo> currentChannel;
	// How many *enabled* rows in the whole `channels` table have
	// login_gateway = true. This is a static, single-snapshot check (every
	// process reloads the same table) - it does not require live
	// cross-process communication, unlike the runtime-heartbeat-based
	// "is another process's login gateway actually alive" check, which
	// remains 📐 (see docs/multichannel/ARCHITECTURE.md §4.4).
	int32_t enabledLoginGatewayCount = 0;
	// Result of the caller performing a real, synchronous IRedisClient::
	// ping() against the just-constructed Redis client, *before* calling
	// validate() - kept as a plain input rather than doing the live I/O
	// inside this function, preserving full unit-testability without
	// touching a real Redis. std::nullopt means "no ping was attempted",
	// which validate() treats as equivalent to a failure whenever a ping
	// would have been required (multiChannelEnabled && redisClientCompiledIn) -
	// "never attempted" must not silently pass as "succeeded".
	std::optional<RedisPingOutcome> redisPingOutcome;
};

struct ClusterConfigValidationResult {
	// Fail-closed: valid is false if any hard-failure check did not pass.
	// An empty errors list with valid == true means single-channel mode
	// (validation is a no-op) or every check passed.
	bool valid = true;
	std::vector<ClusterConfigValidationError> errors;
	// Soft, non-fatal recommendations (e.g. "lease TTL should be at least
	// 2x the heartbeat interval") - logged as warnings by the caller, never
	// block startup.
	std::vector<std::string> warnings;
};

// Fail-closed startup validation for multi-channel mode (spec §4.4). Pure
// function over caller-supplied values so it's fully unit-testable without
// touching Redis/DB/the real ConfigManager; the real startup sequence
// (Phase 2 hook) is expected to gather these inputs and abort the process
// if `valid` is false, per docs/multichannel/ARCHITECTURE.md §4.4.
class ClusterConfigValidator {
public:
	[[nodiscard]] static ClusterConfigValidationResult validate(const ClusterConfigValidationInput &input);
};
