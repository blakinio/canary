/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_region_pool.hpp"

namespace {
	InstanceMapRegion makeRegion(uint32_t slot, uint16_t minX, uint16_t minY, uint8_t minZ = 7, uint16_t size = 10, uint8_t maxZ = 7) {
		return {
			.slot = toSlotId(slot),
			.minX = minX,
			.minY = minY,
			.minZ = minZ,
			.maxX = static_cast<uint16_t>(minX + size - 1),
			.maxY = static_cast<uint16_t>(minY + size - 1),
			.maxZ = maxZ,
			.name = "region-" + std::to_string(slot),
		};
	}
}

TEST(InstanceMapRegionTest, ValidatesContainsAndThreeDimensionalOverlap) {
	const auto first = makeRegion(0, 100, 100, 7, 10, 8);
	const auto adjacent = makeRegion(1, 110, 100, 7, 10, 8);
	const auto sameCoordinatesDifferentFloor = makeRegion(2, 100, 100, 9, 10, 9);
	const auto overlapping = makeRegion(3, 109, 109, 8, 10, 8);

	EXPECT_TRUE(first.isValid());
	EXPECT_TRUE(first.contains(100, 100, 7));
	EXPECT_TRUE(first.contains(109, 109, 8));
	EXPECT_FALSE(first.contains(110, 109, 8));
	EXPECT_FALSE(first.overlaps(adjacent));
	EXPECT_FALSE(first.overlaps(sameCoordinatesDifferentFloor));
	EXPECT_TRUE(first.overlaps(overlapping));
}

TEST(InstanceRegionPoolTest, RejectsInvalidDuplicateAndOverlappingRegions) {
	auto invalidSlot = makeRegion(0, 100, 100);
	invalidSlot.slot = InstanceSlotId::Invalid;
	EXPECT_THROW(InstanceRegionPool({ invalidSlot }), std::invalid_argument);

	auto inverted = makeRegion(0, 100, 100);
	inverted.maxX = 99;
	EXPECT_THROW(InstanceRegionPool({ inverted }), std::invalid_argument);

	auto invalidFloor = makeRegion(0, 100, 100);
	invalidFloor.maxZ = static_cast<uint8_t>(INSTANCE_MAP_MAX_Z + 1);
	EXPECT_THROW(InstanceRegionPool({ invalidFloor }), std::invalid_argument);

	EXPECT_THROW(InstanceRegionPool({ makeRegion(0, 100, 100), makeRegion(0, 200, 200) }), std::invalid_argument);
	EXPECT_THROW(InstanceRegionPool({ makeRegion(0, 100, 100), makeRegion(1, 109, 109) }), std::invalid_argument);
}

TEST(InstanceRegionPoolTest, ReservesReleasesAndReusesConfiguredRegions) {
	InstanceRegionPool pool({ makeRegion(4, 100, 100), makeRegion(9, 200, 200) });

	EXPECT_EQ(pool.totalCount(), 2);
	EXPECT_EQ(pool.availableCount(), 2);

	const auto first = pool.reserve();
	ASSERT_TRUE(first.ok);
	EXPECT_EQ(first.slot, toSlotId(4));
	ASSERT_TRUE(first.region.has_value());
	EXPECT_EQ(first.region->name, "region-4");
	EXPECT_TRUE(pool.isReserved(toSlotId(4)));
	EXPECT_FALSE(pool.reserve(toSlotId(4)));

	EXPECT_TRUE(pool.reserve(toSlotId(9)));
	EXPECT_EQ(pool.availableCount(), 0);
	EXPECT_FALSE(pool.reserve().ok);

	EXPECT_TRUE(pool.release(toSlotId(4)));
	EXPECT_FALSE(pool.release(toSlotId(4)));
	EXPECT_FALSE(pool.release(toSlotId(999)));

	const auto reused = pool.reserve();
	ASSERT_TRUE(reused.ok);
	EXPECT_EQ(reused.slot, toSlotId(4));
}

TEST(InstanceRegionPoolTest, ReturnsConfiguredRegionWithoutRequiringReservation) {
	InstanceRegionPool pool({ makeRegion(7, 32000, 32000, 6, 20, 8) });

	const auto region = pool.getRegion(toSlotId(7));
	ASSERT_TRUE(region.has_value());
	EXPECT_TRUE(region->contains(32010, 32010, 7));
	EXPECT_FALSE(pool.getRegion(toSlotId(8)).has_value());
}

TEST(InstanceRegionPoolTest, ConcurrentReservationsNeverReturnTheSameSlot) {
	std::vector<InstanceMapRegion> regions;
	for (uint32_t slot = 0; slot < 8; ++slot) {
		regions.push_back(makeRegion(slot, static_cast<uint16_t>(100 + slot * 20), 100));
	}
	InstanceRegionPool pool(std::move(regions));

	std::mutex resultMutex;
	std::vector<InstanceSlotId> reserved;
	std::vector<std::thread> workers;
	for (std::size_t index = 0; index < 24; ++index) {
		workers.emplace_back([&] {
			const auto result = pool.reserve();
			if (result.ok) {
				std::scoped_lock lock(resultMutex);
				reserved.push_back(result.slot);
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	ASSERT_EQ(reserved.size(), 8);
	std::sort(reserved.begin(), reserved.end(), [](InstanceSlotId lhs, InstanceSlotId rhs) {
		return toIndex(lhs) < toIndex(rhs);
	});
	const auto uniqueEnd = std::unique(reserved.begin(), reserved.end());
	EXPECT_EQ(uniqueEnd, reserved.end());
	EXPECT_EQ(pool.availableCount(), 0);
}
