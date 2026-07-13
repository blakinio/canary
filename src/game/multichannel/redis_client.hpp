/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/channel_runtime_status.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
	#include <string>
#endif

// Categorized outcome of a live PING (docs/multichannel/ARCHITECTURE.md
// §4.4): "the client object was constructed" and "the config was present"
// are not proof Redis is actually reachable - only a real round-trip is.
// Deliberately coarser than raw hiredis error codes (which do not always
// distinguish DNS failure from connection refused from a bare I/O error
// across platforms/versions); each category maps to hiredis's best
// available signal, with the exact library-reported string always logged
// separately by the caller for full diagnostic value.
enum class RedisPingOutcome : uint8_t {
	Success,
	DnsFailure,
	ConnectionRefused,
	Timeout,
	AuthenticationFailed,
	UnexpectedResponse,
	Other,
};

struct RedisPingResult {
	RedisPingOutcome outcome = RedisPingOutcome::Other;
	// Raw, human-readable diagnostic (e.g. the hiredis errstr) for logging
	// only - never parsed/matched on by callers, since the exact wording is
	// not a stable contract.
	std::string detail;
};

struct LeaseAcquireOutcome {
	bool acquired = false;
	std::string sessionId;
	uint64_t fencingToken = 0;
};

struct LeaseRenewOutcome {
	bool renewed = false;
	uint64_t fencingToken = 0;
};

// Abstraction over the atomic Redis operations used by the multi-channel
// coordination layer. Session lease methods correspond 1:1 to the Lua scripts
// in redis_scripts/. Runtime heartbeat writes are also atomic (HSET + PEXPIRE
// in one script), while reads are fail-closed by the runtime registry.
class IRedisClient {
public:
	virtual ~IRedisClient() = default;

	// Atomically acquires the lease at lockKey if unheld or expired. On
	// success, issues a fencing token that is monotonically increasing for
	// the lifetime of lockKey.
	virtual LeaseAcquireOutcome acquireLease(const std::string &lockKey, const std::string &sessionId, const std::string &channelId, const std::string &instanceId, int64_t ttlMs, int64_t nowMs) = 0;

	// Atomically extends the lease's expiry, but only if sessionId is still
	// the current holder and the lease had not already expired.
	virtual LeaseRenewOutcome renewLease(const std::string &lockKey, const std::string &sessionId, int64_t ttlMs, int64_t nowMs) = 0;

	// Atomically releases the lease, but only if sessionId is still the
	// current holder. The fencing token counter is preserved.
	virtual bool releaseLease(const std::string &lockKey, const std::string &sessionId) = 0;

	// Read-only: the current fencing token for lockKey, if any has ever been
	// issued.
	virtual std::optional<uint64_t> peekFencingToken(const std::string &lockKey) = 0;

	// Publishes the complete runtime record and applies its TTL atomically.
	// nowMs is part of the interface so deterministic fakes can model expiry;
	// Redis itself uses PEXPIRE and does not need the caller's clock.
	virtual bool writeChannelRuntimeStatus(const std::string &runtimeKey, const ChannelRuntimeStatus &status, int64_t ttlMs, int64_t nowMs) = 0;

	// Reads one runtime record. Missing/expired keys return nullopt while
	// keeping isHealthy()==true; transport/protocol failure returns nullopt and
	// sets isHealthy()==false so callers can distinguish absence from outage.
	virtual std::optional<ChannelRuntimeStatus> readChannelRuntimeStatus(const std::string &runtimeKey, int64_t nowMs) = 0;

	// True if the connection itself is currently usable.
	[[nodiscard]] virtual bool isHealthy() const = 0;

	// Performs a real, synchronous round-trip (connect if needed, then
	// PING) against the configured server. Distinct from isHealthy(), which
	// only reflects whichever *other* operation last ran - this is the one
	// method whose entire purpose is proving reachability right now, used
	// once at startup by ClusterConfigValidator's caller
	// (docs/multichannel/ARCHITECTURE.md §4.4) so "Redis is configured" is
	// never confused with "Redis is actually reachable."
	[[nodiscard]] virtual RedisPingResult ping() = 0;
};
