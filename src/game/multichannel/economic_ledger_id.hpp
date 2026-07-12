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
	#include <string>
#endif

// Pure, dependency-free deterministic-UUID construction for
// `economic_ledger.transaction_uuid` (docs/multichannel/ARCHITECTURE.md
// §8). Kept in its own header, separate from EconomicLedgerStore, so it
// can be unit-tested without pulling in that class's database.hpp
// dependency - the same reasoning as position_serialization.hpp being
// split out of channel_switch_audit_store.hpp.
namespace multichannel {
	[[nodiscard]] std::string computeDeterministicLedgerUuid(const std::string &namespaceTag, uint64_t naturalKey);
} // namespace multichannel
