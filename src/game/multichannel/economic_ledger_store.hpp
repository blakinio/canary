/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
	#include <string>
#endif

// Read/write access to the `economic_ledger` table (docs/multichannel/
// ARCHITECTURE.md §8): `transaction_uuid` as PRIMARY KEY is the
// idempotency mechanism - a retried operation re-inserts the same UUID
// and gets a duplicate-key error (or, via beginPending's return value,
// a clean "already handled, do not reapply") instead of a second effect.
struct EconomicLedgerRecord {
	std::string transactionUuid;
	std::string operationType;
	std::optional<int32_t> accountId;
	std::optional<int32_t> playerId;
	std::optional<int32_t> sourceChannelId;
	std::optional<int32_t> targetChannelId;
	int64_t amount = 0;
	std::string currency = "gold";
	std::optional<int32_t> itemId;
	std::optional<int32_t> itemCount;
};

class EconomicLedgerStore {
public:
	// Inserts a PENDING row for transactionUuid. Returns false both when
	// the UUID already exists (a genuine replay of an already-attempted
	// operation) and on a real DB error - the caller must treat both the
	// same way: do not perform the money/item effect this call is meant to
	// guard, since either result means "this operation is not safely known
	// to be first-time-only" and financial code must fail closed, not
	// guess.
	static bool beginPending(const EconomicLedgerRecord &record, int64_t nowMs);

	static bool markCommitted(const std::string &transactionUuid, int64_t nowMs);
	static bool markFailed(const std::string &transactionUuid, int64_t nowMs);

	// A stable, deterministic, UUID-*shaped* (36-char) string derived from
	// a namespace tag and a natural key (e.g. a market offer's own row id) -
	// not a real RFC 4122 UUID, just something that fits the
	// `transaction_uuid CHAR(36)` column and is guaranteed to come out
	// identical every time for the same (namespaceTag, naturalKey) pair.
	// This is what makes an idempotent background job (no per-attempt
	// randomness available) able to use the same PRIMARY KEY-based replay
	// protection as a live, request-scoped operation would generate a
	// random UUID for. Pure and dependency-free, exposed for unit testing.
	[[nodiscard]] static std::string deterministicUuid(const std::string &namespaceTag, uint64_t naturalKey);
};
