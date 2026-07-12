/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_region_pool.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <stdexcept>
	#include <utility>
#endif

bool InstanceMapRegion::isValid() const noexcept {
	return slot != InstanceSlotId::Invalid && minX <= maxX && minY <= maxY && minZ <= maxZ && maxZ <= INSTANCE_MAP_MAX_Z;
}

bool InstanceMapRegion::contains(uint16_t x, uint16_t y, uint8_t z) const noexcept {
	return x >= minX && x <= maxX && y >= minY && y <= maxY && z >= minZ && z <= maxZ;
}

bool InstanceMapRegion::overlaps(const InstanceMapRegion &other) const noexcept {
	const bool overlapsX = minX <= other.maxX && other.minX <= maxX;
	const bool overlapsY = minY <= other.maxY && other.minY <= maxY;
	const bool overlapsZ = minZ <= other.maxZ && other.minZ <= maxZ;
	return overlapsX && overlapsY && overlapsZ;
}

InstanceRegionPool::InstanceRegionPool(std::vector<InstanceMapRegion> regions) {
	entries.reserve(regions.size());
	for (auto &region : regions) {
		if (!region.isValid()) {
			throw std::invalid_argument("invalid instance map region for slot " + std::to_string(toIndex(region.slot)));
		}

		for (const auto &entry : entries) {
			if (entry.region.slot == region.slot) {
				throw std::invalid_argument("duplicate instance region slot " + std::to_string(toIndex(region.slot)));
			}
			if (entry.region.overlaps(region)) {
				throw std::invalid_argument(
					"instance regions overlap: slots " + std::to_string(toIndex(entry.region.slot)) + " and " + std::to_string(toIndex(region.slot))
				);
			}
		}

		entries.push_back({ .region = std::move(region), .reserved = false });
	}
}

InstanceRegionPool::Entry* InstanceRegionPool::findEntryLocked(InstanceSlotId slot) {
	for (auto &entry : entries) {
		if (entry.region.slot == slot) {
			return &entry;
		}
	}
	return nullptr;
}

const InstanceRegionPool::Entry* InstanceRegionPool::findEntryLocked(InstanceSlotId slot) const {
	for (const auto &entry : entries) {
		if (entry.region.slot == slot) {
			return &entry;
		}
	}
	return nullptr;
}

InstanceRegionPool::ReserveResult InstanceRegionPool::reserve() {
	std::scoped_lock lock(mutex);
	for (auto &entry : entries) {
		if (!entry.reserved) {
			entry.reserved = true;
			return {
				.ok = true,
				.slot = entry.region.slot,
				.region = entry.region,
				.error = {},
			};
		}
	}
	return { .ok = false, .slot = InstanceSlotId::Invalid, .region = std::nullopt, .error = "no available instance regions" };
}

bool InstanceRegionPool::reserve(InstanceSlotId slot) {
	std::scoped_lock lock(mutex);
	auto* entry = findEntryLocked(slot);
	if (!entry || entry->reserved) {
		return false;
	}
	entry->reserved = true;
	return true;
}

bool InstanceRegionPool::release(InstanceSlotId slot) {
	std::scoped_lock lock(mutex);
	auto* entry = findEntryLocked(slot);
	if (!entry || !entry->reserved) {
		return false;
	}
	entry->reserved = false;
	return true;
}

std::optional<InstanceMapRegion> InstanceRegionPool::getRegion(InstanceSlotId slot) const {
	std::scoped_lock lock(mutex);
	const auto* entry = findEntryLocked(slot);
	if (!entry) {
		return std::nullopt;
	}
	return entry->region;
}

bool InstanceRegionPool::isReserved(InstanceSlotId slot) const {
	std::scoped_lock lock(mutex);
	const auto* entry = findEntryLocked(slot);
	return entry && entry->reserved;
}

std::size_t InstanceRegionPool::availableCount() const {
	std::scoped_lock lock(mutex);
	std::size_t count = 0;
	for (const auto &entry : entries) {
		if (!entry.reserved) {
			++count;
		}
	}
	return count;
}

std::size_t InstanceRegionPool::totalCount() const {
	return entries.size();
}
