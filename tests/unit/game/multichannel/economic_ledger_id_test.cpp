/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/economic_ledger_id.hpp"

#include <gtest/gtest.h>
#include <unordered_set>

TEST(EconomicLedgerIdTest, ProducesA36CharacterUuidShapedString) {
	const auto uuid = multichannel::computeDeterministicLedgerUuid("market.expire", 42);
	EXPECT_EQ(36u, uuid.size());
	// 8-4-4-4-12 layout.
	EXPECT_EQ('-', uuid[8]);
	EXPECT_EQ('-', uuid[13]);
	EXPECT_EQ('-', uuid[18]);
	EXPECT_EQ('-', uuid[23]);
}

TEST(EconomicLedgerIdTest, IsDeterministicForTheSameInputs) {
	const auto first = multichannel::computeDeterministicLedgerUuid("market.expire", 42);
	const auto second = multichannel::computeDeterministicLedgerUuid("market.expire", 42);
	EXPECT_EQ(first, second);
}

TEST(EconomicLedgerIdTest, DiffersForDifferentNaturalKeys) {
	const auto a = multichannel::computeDeterministicLedgerUuid("market.expire", 1);
	const auto b = multichannel::computeDeterministicLedgerUuid("market.expire", 2);
	EXPECT_NE(a, b);
}

TEST(EconomicLedgerIdTest, DiffersForDifferentNamespaceTagsWithTheSameNaturalKey) {
	const auto a = multichannel::computeDeterministicLedgerUuid("market.expire", 42);
	const auto b = multichannel::computeDeterministicLedgerUuid("mail.deliver", 42);
	EXPECT_NE(a, b);
}

TEST(EconomicLedgerIdTest, NoCollisionsAcrossASequentialRangeOfNaturalKeys) {
	std::unordered_set<std::string> seen;
	for (uint64_t key = 0; key < 10000; ++key) {
		seen.insert(multichannel::computeDeterministicLedgerUuid("market.expire", key));
	}
	EXPECT_EQ(10000u, seen.size());
}
