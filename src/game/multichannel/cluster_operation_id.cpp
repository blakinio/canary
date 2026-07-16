/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_operation_id.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <iomanip>
	#include <random>
	#include <sstream>
#endif

std::string multichannel::generateRandomOperationId() {
	// Same non-cryptographic rationale as ClusterSessionManager::
	// generateSessionId(): this is a replay/idempotency tag, not a
	// security credential.
	static thread_local std::mt19937_64 engine(std::random_device {}());
	std::uniform_int_distribution<uint64_t> distribution;

	const uint64_t high = distribution(engine);
	const uint64_t low = distribution(engine);

	// Standard 8-4-4-4-12 UUID layout (36 characters), matching
	// EconomicLedgerStore::deterministicUuid's shape so both random and
	// deterministic operation_id values look consistent in the same
	// CHAR(36) column.
	std::ostringstream stream;
	stream << std::hex << std::setfill('0')
		   << std::setw(8) << static_cast<uint32_t>(high >> 32) << '-'
		   << std::setw(4) << static_cast<uint16_t>(high >> 16) << '-'
		   << std::setw(4) << static_cast<uint16_t>(high & 0xFFFF) << '-'
		   << std::setw(4) << static_cast<uint16_t>(low >> 48) << '-'
		   << std::setw(12) << (low & 0xFFFFFFFFFFFFULL);
	return stream.str();
}
