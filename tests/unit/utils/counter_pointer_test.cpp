/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "lib/di/container.hpp"
#include "utils/counter_pointer.hpp"

// SharedPtrManager::getInstance() used to be a hand-rolled Meyers singleton
// (a function-local static). It now goes through the same inject<T>()
// container every other migrated g_*() accessor uses. These tests pin down
// the two properties that migration is supposed to give us without changing
// anything else: the default-container behavior stays exactly what a Meyers
// singleton already gave every caller (same shared instance every time), and
// a test can now get an isolated instance instead, without SharedPtrManager
// itself knowing anything about it.
TEST(SharedPtrManagerDiMigrationTest, DefaultContainerBehavesLikeTheOldMeyersSingleton) {
	SharedPtrManager &first = SharedPtrManager::getInstance();
	SharedPtrManager &second = g_counterPointer();
	EXPECT_EQ(&first, &second);
}

TEST(SharedPtrManagerDiMigrationTest, TestContainerYieldsAnInstanceIsolatedFromProduction) {
	SharedPtrManager &productionInstance = SharedPtrManager::getInstance();

	auto* previousContainer = DI::getTestContainer();
	di::extension::injector<> testInjector {};
	DI::setTestContainer(&testInjector);
	SharedPtrManager &testInstance = SharedPtrManager::getInstance();
	DI::setTestContainer(previousContainer);

	EXPECT_NE(&productionInstance, &testInstance);
}

TEST(SharedPtrManagerTest, StoreAndCleanDoesNotCrashOnLiveOrExpiredPointers) {
	di::extension::injector<> testInjector {};
	auto* previousContainer = DI::getTestContainer();
	DI::setTestContainer(&testInjector);

	SharedPtrManager &manager = SharedPtrManager::getInstance();
	auto alive = std::make_shared<int>(42);
	manager.store("alive", alive);
	{
		auto expiring = std::make_shared<int>(7);
		manager.store("expiring", expiring);
	}

	manager.countAllReferencesAndClean();
	manager.countAllReferencesAndClean();

	DI::setTestContainer(previousContainer);
}
