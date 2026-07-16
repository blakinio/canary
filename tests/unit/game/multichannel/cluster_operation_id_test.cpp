/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_operation_id.hpp"

#include <gtest/gtest.h>
#include <set>

TEST(ClusterOperationIdTest, ProducesThirtySixCharacterUuidShape) {
	const auto id = multichannel::generateRandomOperationId();
	EXPECT_EQ(36u, id.size());
	EXPECT_EQ('-', id[8]);
	EXPECT_EQ('-', id[13]);
	EXPECT_EQ('-', id[18]);
	EXPECT_EQ('-', id[23]);
}

TEST(ClusterOperationIdTest, EveryCharacterIsHexOrDash) {
	const auto id = multichannel::generateRandomOperationId();
	for (const char character : id) {
		EXPECT_TRUE(character == '-' || std::isxdigit(static_cast<unsigned char>(character))) << "unexpected character: " << character;
	}
}

TEST(ClusterOperationIdTest, RepeatedCallsAreNotIdentical) {
	std::set<std::string> ids;
	for (int i = 0; i < 1000; ++i) {
		ids.insert(multichannel::generateRandomOperationId());
	}
	// No collisions across 1000 draws from a 128-bit random space.
	EXPECT_EQ(1000u, ids.size());
}
