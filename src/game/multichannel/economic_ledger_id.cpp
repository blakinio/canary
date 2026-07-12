/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/economic_ledger_id.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <iomanip>
	#include <sstream>
#endif

namespace {
	// FNV-1a 64-bit - the same simple, non-cryptographic, dependency-free
	// hash already used by ChannelRegistry::hashBytes (this is a
	// determinism/collision-avoidance tool, not a security boundary).
	uint64_t fnv1a64(const std::string &value) {
		constexpr uint64_t offsetBasis = 0xcbf29ce484222325ULL;
		constexpr uint64_t prime = 0x100000001b3ULL;
		uint64_t hash = offsetBasis;
		for (const unsigned char byte : value) {
			hash ^= byte;
			hash *= prime;
		}
		return hash;
	}
} // namespace

std::string multichannel::computeDeterministicLedgerUuid(const std::string &namespaceTag, uint64_t naturalKey) {
	const uint64_t namespaceHash = fnv1a64(namespaceTag);

	// Standard 8-4-4-4-12 UUID layout (36 characters), populated
	// deterministically rather than randomly: the first two groups come
	// from the namespace tag's hash (so different operation types sharing
	// a numerically identical naturalKey can never collide), the last two
	// groups come from naturalKey itself (so the same natural key always
	// reproduces the exact same string). Not a real RFC 4122 UUID - it
	// only needs to be a stable, unique-enough 36-character value that
	// fits the `transaction_uuid CHAR(36)` column.
	std::ostringstream stream;
	stream << std::hex << std::setfill('0')
		   << std::setw(8) << static_cast<uint32_t>(namespaceHash >> 32) << '-'
		   << std::setw(4) << static_cast<uint16_t>(namespaceHash >> 16) << '-'
		   << std::setw(4) << static_cast<uint16_t>(namespaceHash & 0xFFFF) << '-'
		   << std::setw(4) << static_cast<uint16_t>((naturalKey >> 48) & 0xFFFF) << '-'
		   << std::setw(12) << (naturalKey & 0xFFFFFFFFFFFFULL);
	return stream.str();
}
