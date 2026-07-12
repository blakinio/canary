/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "lib/di/container.hpp"
#include "lua/scripts/scripts.hpp"

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

TEST(ScriptsDiMigrationTest, DefaultContainerReturnsTheSameScriptsInstance) {
	Scripts &first = Scripts::getInstance();
	Scripts &second = g_scripts();
	EXPECT_EQ(&first, &second);
}

TEST(ScriptsDiMigrationTest, TestContainerProvidesAnIsolatedScriptsInstance) {
	Scripts &productionInstance = Scripts::getInstance();
	di::extension::injector<> testInjector {};

	TestContainerScope scope(&testInjector);
	Scripts &testInstance = Scripts::getInstance();

	EXPECT_NE(&productionInstance, &testInstance);
}
