/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include "creatures/players/player.hpp"
#include "creatures/players/components/wheel/wheel_gems.hpp"
#include "enums/player_wheel.hpp"
#include "lib/di/container.hpp"
#include "lib/logging/in_memory_logger.hpp"

class WheelValidationTest : public ::testing::Test {
protected:
	static void SetUpTestSuite() {
		previousTestContainer = DI::getTestContainer();
		InMemoryLogger::install(injector);
		DI::setTestContainer(&injector);
	}

	static void TearDownTestSuite() {
		DI::setTestContainer(previousTestContainer);
	}

	static std::shared_ptr<Player> makePlayer(uint32_t level) {
		auto player = std::make_shared<Player>();
		player->setLevel(level);
		return player;
	}

	inline static di::extension::injector<> injector {};
	inline static di::extension::injector<>* previousTestContainer = nullptr;
};

TEST_F(WheelValidationTest, LevelPointsStartAfterLevelFifty) {
	EXPECT_EQ(0, makePlayer(1)->wheel().getWheelPoints());
	EXPECT_EQ(0, makePlayer(50)->wheel().getWheelPoints());
	EXPECT_EQ(1, makePlayer(51)->wheel().getWheelPoints());
	EXPECT_EQ(50, makePlayer(100)->wheel().getWheelPoints());
}

TEST_F(WheelValidationTest, InvalidOverspentStateDoesNotUnderflowUnusedPoints) {
	auto player = makePlayer(51);
	player->wheel().setPointsBySlotType(enumToValue(WheelSlots_t::SLOT_GREEN_50), 50);
	EXPECT_EQ(0, player->wheel().getUnusedPoints());
}

TEST_F(WheelValidationTest, SupremeGradeCostsMatchTheSkillWheelContract) {
	auto player = makePlayer(51);

	const auto [gradeOneGold, gradeOneFragments] = player->wheel().getGreaterGradeCost(1);
	EXPECT_EQ(5000000, gradeOneGold);
	EXPECT_EQ(5, gradeOneFragments);

	const auto [gradeTwoGold, gradeTwoFragments] = player->wheel().getGreaterGradeCost(2);
	EXPECT_EQ(12500000, gradeTwoGold);
	EXPECT_EQ(15, gradeTwoFragments);

	const auto [gradeThreeGold, gradeThreeFragments] = player->wheel().getGreaterGradeCost(3);
	EXPECT_EQ(75000000, gradeThreeGold);
	EXPECT_EQ(30, gradeThreeFragments);
}

TEST_F(WheelValidationTest, InvalidGradeHasNoCost) {
	auto player = makePlayer(51);
	const auto [gold, fragments] = player->wheel().getGreaterGradeCost(4);
	EXPECT_EQ(0, gold);
	EXPECT_EQ(0, fragments);
}

TEST_F(WheelValidationTest, GemGradesAreLimitedByPreviousSlots) {
	EXPECT_EQ((std::array<uint8_t, 3> { 3, 0, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Lesser, 3, 3, 3));
	EXPECT_EQ((std::array<uint8_t, 3> { 1, 1, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Regular, 1, 3, 3));
	EXPECT_EQ((std::array<uint8_t, 3> { 3, 2, 2 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Greater, 3, 2, 3));
	EXPECT_EQ((std::array<uint8_t, 3> { 0, 0, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Greater, 0, 3, 3));
}

TEST_F(WheelValidationTest, FullVesselResonanceAddsQualityBonusOnlyWhenComplete) {
	EXPECT_EQ(0, WheelGemUtils::getFullResonanceBonus(WheelGemQuality_t::Lesser, 0));
	EXPECT_EQ(1, WheelGemUtils::getFullResonanceBonus(WheelGemQuality_t::Lesser, 1));
	EXPECT_EQ(0, WheelGemUtils::getFullResonanceBonus(WheelGemQuality_t::Regular, 1));
	EXPECT_EQ(1, WheelGemUtils::getFullResonanceBonus(WheelGemQuality_t::Regular, 2));
	EXPECT_EQ(0, WheelGemUtils::getFullResonanceBonus(WheelGemQuality_t::Greater, 2));
	EXPECT_EQ(2, WheelGemUtils::getFullResonanceBonus(WheelGemQuality_t::Greater, 3));
}
