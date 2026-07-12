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

namespace {
	class TestContainerScope final {
	public:
		explicit TestContainerScope(di::extension::injector<>* container) :
			previousContainer(DI::getTestContainer()) {
			DI::setTestContainer(container);
		}

		~TestContainerScope() {
			DI::setTestContainer(previousContainer);
		}

		TestContainerScope(const TestContainerScope &) = delete;
		TestContainerScope &operator=(const TestContainerScope &) = delete;

	private:
		di::extension::injector<>* previousContainer;
	};
}

TEST(SharedPtrManagerDiMigrationTest, DefaultContainerBehavesLikeTheOldMeyersSingleton) {
	SharedPtrManager &first = SharedPtrManager::getInstance();
	SharedPtrManager &second = g_counterPointer();
	EXPECT_EQ(&first, &second);
}

TEST(SharedPtrManagerDiMigrationTest, TestContainerYieldsAnInstanceIsolatedFromProduction) {
	SharedPtrManager &productionInstance = SharedPtrManager::getInstance();
	di::extension::injector<> testInjector {};

	TestContainerScope scope(&testInjector);
	SharedPtrManager &testInstance = SharedPtrManager::getInstance();

	EXPECT_NE(&productionInstance, &testInstance);
}

TEST(SharedPtrManagerTest, StoreAndCleanDoesNotCrashOnLiveOrExpiredPointers) {
	SharedPtrManager &manager = SharedPtrManager::getInstance();
	auto alive = std::make_shared<int>(42);
	manager.store("SharedPtrManagerTest.alive", alive);
	{
		auto expiring = std::make_shared<int>(7);
		manager.store("SharedPtrManagerTest.expiring", expiring);
	}

	manager.countAllReferencesAndClean();
	manager.countAllReferencesAndClean();

	alive.reset();
	manager.countAllReferencesAndClean();
}
