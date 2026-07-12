/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <cstdint>
#endif

namespace multichannel {
	// Current wall-clock time in milliseconds since the Unix epoch. Shared by
	// every multichannel module that previously defined its own identical
	// anonymous-namespace copy of this helper (channel_registry.cpp,
	// channel_switch_service.cpp, cluster_runtime.cpp) - with unity builds
	// enabled, those per-file anonymous-namespace definitions land in the
	// same translation unit and collide (a real redefinition build failure
	// on every non-Linux-debug CI target). A single `inline` definition is
	// the fix: identical inline functions in multiple translation units are
	// explicitly permitted to merge under the ODR.
	inline int64_t wallClockMs() {
		return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
	}
} // namespace multichannel
