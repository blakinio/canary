/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include "game/functions/forge_transaction.hpp"

TEST(ForgeTransactionTest, CommitsAllStepsWithoutRollback) {
	std::vector<int> events;
	ForgeTransaction transaction;
	transaction.stage(
		[&events] {
			events.push_back(1);
			return true;
		},
		[&events] { events.push_back(-1); }
	);
	transaction.stage(
		[&events] {
			events.push_back(2);
			return true;
		},
		[&events] { events.push_back(-2); }
	);

	EXPECT_TRUE(transaction.commit());
	EXPECT_TRUE(transaction.isCommitted());
	EXPECT_EQ((std::vector<int> { 1, 2 }), events);
}

TEST(ForgeTransactionTest, RollsBackFailedStepAndPriorStepsInReverseOrder) {
	std::vector<int> events;
	ForgeTransaction transaction;
	transaction.stage(
		[&events] {
			events.push_back(1);
			return true;
		},
		[&events] { events.push_back(-1); }
	);
	transaction.stage(
		[&events] {
			events.push_back(2);
			return false;
		},
		[&events] { events.push_back(-2); }
	);
	transaction.stage(
		[&events] {
			events.push_back(3);
			return true;
		},
		[&events] { events.push_back(-3); }
	);

	EXPECT_FALSE(transaction.commit());
	EXPECT_FALSE(transaction.isCommitted());
	EXPECT_EQ((std::vector<int> { 1, 2, -2, -1 }), events);
}

TEST(ForgeTransactionTest, CannotCommitTwice) {
	ForgeTransaction transaction;
	transaction.stage([] { return true; }, [] { });

	EXPECT_TRUE(transaction.commit());
	EXPECT_FALSE(transaction.commit());
}
