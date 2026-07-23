/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once
#include "security/login_session_manager.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <cstddef>
	#include <cstdint>
	#include <functional>
	#include <memory>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <string_view>
	#include <unordered_map>
	#include <vector>
#endif

class GameSessionHttpIssuer {
public:
	static constexpr std::size_t MaxRequestBytes = 8192;
	static constexpr std::size_t LoginAttemptIdHexLength = 32;
	static constexpr std::size_t MaxTrackedLoginAttempts = 4096;
	static constexpr std::chrono::milliseconds DefaultRequestTimeout { 5000 };

	struct Config {
		bool enabled = false;
		std::string bindAddress;
		uint16_t port = 0;
		std::string serviceTokenSha256;
		std::chrono::milliseconds requestTimeout = DefaultRequestTimeout;
	};

	struct CreateRequest {
		int32_t protocolVersion = 0;
		uint32_t accountId = 0;
		int64_t worldId = 0;
		std::string loginAttemptId;
	};

	enum class CreateStatus : uint8_t {
		Ok,
		InvalidRequest,
		WrongWorld,
		DuplicateAttempt,
		AccountUnavailable,
		NoCharacters,
		IssueFailed,
	};

	struct CreateResult {
		CreateStatus status = CreateStatus::InvalidRequest;
		std::string credential;
		std::chrono::system_clock::time_point expiresAt {};
	};

	struct Dependencies {
		std::function<std::optional<std::vector<std::string>>(uint32_t)> loadCharacters;
		std::function<std::optional<std::string>(const LoginSessionIssueParams &)> issueToken;
		std::function<int64_t()> currentWorldId;
		std::function<std::chrono::system_clock::time_point()> now;
	};

	GameSessionHttpIssuer(Config config, Dependencies dependencies);
	~GameSessionHttpIssuer();

	GameSessionHttpIssuer(const GameSessionHttpIssuer &) = delete;
	GameSessionHttpIssuer &operator=(const GameSessionHttpIssuer &) = delete;

	[[nodiscard]] static std::optional<Config> loadConfigFromEnvironment(std::string &error);
	[[nodiscard]] static Dependencies productionDependencies();

	[[nodiscard]] bool start();
	void stop();
	[[nodiscard]] bool isRunning() const;

	// Exposed as deterministic seams for focused unit coverage. The network
	// boundary delegates to these methods and never logs the presented bearer
	// credential or the returned Game Session credential.
	[[nodiscard]] bool authenticateBearer(std::string_view credential) const;
	[[nodiscard]] CreateResult createSession(const CreateRequest &request) const;

private:
	class Impl;

	enum class LoginAttemptReservation : uint8_t {
		Reserved,
		Duplicate,
		CapacityExceeded,
	};

	[[nodiscard]] LoginAttemptReservation reserveLoginAttempt(const std::string &loginAttemptId, std::chrono::system_clock::time_point now) const;
	void releaseLoginAttempt(const std::string &loginAttemptId) const;

	Config config;
	Dependencies dependencies;
	std::unique_ptr<Impl> impl;
	mutable std::mutex loginAttemptsMutex;
	mutable std::unordered_map<std::string, std::chrono::system_clock::time_point> loginAttempts;
};
