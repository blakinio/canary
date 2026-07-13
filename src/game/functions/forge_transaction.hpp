/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include <functional>
#include <utility>
#include <vector>

class ForgeTransaction final {
public:
	using CommitStep = std::function<bool()>;
	using RollbackStep = std::function<void()>;

	void stage(CommitStep commitStep, RollbackStep rollbackStep) {
		steps.emplace_back(std::move(commitStep), std::move(rollbackStep));
	}

	[[nodiscard]] bool commit() {
		if (finished) {
			return false;
		}

		for (size_t index = 0; index < steps.size(); ++index) {
			if (steps[index].commit()) {
				continue;
			}

			rollbackThrough(index);
			finished = true;
			return false;
		}

		finished = true;
		committed = true;
		return true;
	}

	[[nodiscard]] bool isCommitted() const {
		return committed;
	}

private:
	struct Step {
		Step(CommitStep commitStep, RollbackStep rollbackStep) :
			commit(std::move(commitStep)), rollback(std::move(rollbackStep)) { }

		CommitStep commit;
		RollbackStep rollback;
	};

	void rollbackThrough(size_t failedIndex) noexcept {
		for (size_t index = failedIndex + 1; index > 0; --index) {
			try {
				steps[index - 1].rollback();
			} catch (...) {
				// Rollback callbacks must be best-effort and may not escape the
				// transaction boundary. Callers log restoration failures locally.
			}
		}
	}

	std::vector<Step> steps;
	bool finished = false;
	bool committed = false;
};
