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
	#include <string>
#endif

namespace multichannel {
	// A random, UUID-*shaped* (36-char, 8-4-4-4-12) `cluster_pending_
	// operations.operation_id` value, for operations with no natural
	// one-shot source key to derive a deterministic id from (design doc
	// §4.10 - mirrors the same accepted gap already documented for
	// Game::playerCreateMarketOffer). Not a real RFC 4122 UUID, just a
	// stable-shaped, sufficiently-unique value - same philosophy as
	// multichannel::computeDeterministicLedgerUuid, random instead of
	// deterministic. Pure and dependency-free, exposed for unit testing.
	[[nodiscard]] std::string generateRandomOperationId();
} // namespace multichannel
