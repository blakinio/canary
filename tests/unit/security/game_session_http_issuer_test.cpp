/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "security/game_session_http_issuer.hpp"

#include <gtest/gtest.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <optional>
	#include <string>
	#include <utility>
	#include <vector>
#endif

namespace {
	constexpr int32_t WorldId = 7;
	constexpr std::string_view GatewaySecret = "gateway-secret";
	constexpr std::string_view GatewaySecretSha256 = "1e0baae50a6e2006d894f9e64c53a1317e6032f4ba67df08199d5378c5948ce6";
	constexpr std::string_view PreviousGatewaySecret = "previous-gateway-secret";
	constexpr std::string_view PreviousGatewaySecretSha256 = "c0459713d1786d519d9df15a74e111f14ae587a7428c19feee646148de43f6ea";
	const auto FixedNow = std::chrono::system_clock::time_point(std::chrono::seconds(123456));

	GameSessionHttpIssuer::Config makeConfig() {
		GameSessionHttpIssuer::Config config;
		config.enabled = true;
		config.bindAddress = "127.0.0.1";
		config.port = 18080;
		config.serviceTokenSha256 = GatewaySecretSha256;
		return config;
	}

	GameSessionHttpIssuer::CreateRequest makeRequest(uint32_t accountId = 42, int64_t worldId = WorldId) {
		return {
			.protocolVersion = 1,
			.accountId = accountId,
			.worldId = worldId,
			.loginAttemptId = "00112233445566778899aabbccddeeff",
		};
	}

	GameSessionHttpIssuer::Dependencies makeDependencies(
		LoginSessionManager &manager,
		std::optional<std::vector<std::string>> characters = std::vector<std::string> { "Knight", "Druid" },
		int32_t worldId = WorldId
	) {
		GameSessionHttpIssuer::Dependencies dependencies;
		dependencies.loadCharacters = [characters = std::move(characters)](uint32_t) {
			return characters;
		};
		dependencies.issueToken = [&manager](const LoginSessionIssueParams &params) {
			return manager.issueToken(params);
		};
		dependencies.currentWorldId = [worldId] {
			return worldId;
		};
		dependencies.now = [] {
			return FixedNow;
		};
		return dependencies;
	}
}

TEST(GameSessionHttpIssuerTest, BearerAuthenticationUsesConfiguredSha256Hash) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager));

	EXPECT_TRUE(issuer.authenticateBearer(GatewaySecret));
	EXPECT_FALSE(issuer.authenticateBearer("wrong-secret"));
	EXPECT_FALSE(issuer.authenticateBearer(""));
}

TEST(GameSessionHttpIssuerTest, BearerAuthenticationAcceptsPreviousCredentialDuringRotation) {
	LoginSessionManager manager;
	auto config = makeConfig();
	config.previousServiceTokenSha256 = PreviousGatewaySecretSha256;
	GameSessionHttpIssuer issuer(config, makeDependencies(manager));

	EXPECT_TRUE(issuer.authenticateBearer(GatewaySecret));
	EXPECT_TRUE(issuer.authenticateBearer(PreviousGatewaySecret));
	EXPECT_FALSE(issuer.authenticateBearer("wrong-secret"));
}

TEST(GameSessionHttpIssuerTest, DisabledIssuerRejectsBearerAndCreateRequests) {
	LoginSessionManager manager;
	auto config = makeConfig();
	config.enabled = false;
	GameSessionHttpIssuer issuer(config, makeDependencies(manager));

	EXPECT_FALSE(issuer.authenticateBearer(GatewaySecret));
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::InvalidRequest, issuer.createSession(makeRequest()).status);
}

TEST(GameSessionHttpIssuerTest, WrongWorldFailsClosedBeforeTokenIssuance) {
	LoginSessionManager manager;
	int issueCalls = 0;
	auto dependencies = makeDependencies(manager);
	dependencies.issueToken = [&issueCalls](const LoginSessionIssueParams &) -> std::optional<std::string> {
		++issueCalls;
		return "unexpected";
	};
	GameSessionHttpIssuer issuer(makeConfig(), std::move(dependencies));

	const auto result = issuer.createSession(makeRequest(42, WorldId + 1));
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::WrongWorld, result.status);
	EXPECT_EQ(0, issueCalls);
}

TEST(GameSessionHttpIssuerTest, InvalidAccountRequestFailsBeforeLoadingCharacters) {
	LoginSessionManager manager;
	int loadCalls = 0;
	auto dependencies = makeDependencies(manager);
	dependencies.loadCharacters = [&loadCalls](uint32_t) -> std::optional<std::vector<std::string>> {
		++loadCalls;
		return std::vector<std::string> { "Knight" };
	};
	GameSessionHttpIssuer issuer(makeConfig(), std::move(dependencies));

	const auto result = issuer.createSession(makeRequest(0));
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::InvalidRequest, result.status);
	EXPECT_EQ(0, loadCalls);
}

TEST(GameSessionHttpIssuerTest, UnavailableAccountDoesNotIssueToken) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager, std::nullopt));

	const auto result = issuer.createSession(makeRequest());
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::AccountUnavailable, result.status);
	EXPECT_EQ(0u, manager.activeTokenCount());
}

TEST(GameSessionHttpIssuerTest, AccountWithoutCharactersDoesNotIssueToken) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager, std::vector<std::string> {}));

	const auto result = issuer.createSession(makeRequest());
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::NoCharacters, result.status);
	EXPECT_EQ(0u, manager.activeTokenCount());
}

TEST(GameSessionHttpIssuerTest, IssuedCredentialBindsAccountCharactersAndCurrentProfile) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager));

	const auto result = issuer.createSession(makeRequest(42));
	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, result.status);
	ASSERT_FALSE(result.credential.empty());
	EXPECT_EQ(FixedNow + LoginSessionManager::DefaultTtl, result.expiresAt);

	const auto consumed = manager.consumeToken(result.credential, "Knight", ProtocolProfileId::Current);
	EXPECT_TRUE(consumed.ok);
	EXPECT_EQ(42u, consumed.accountId);
}

TEST(GameSessionHttpIssuerTest, DuplicateLoginAttemptDoesNotMintSecondCredential) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager));

	const auto first = issuer.createSession(makeRequest());
	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, first.status);
	EXPECT_EQ(1u, manager.activeTokenCount());

	const auto duplicate = issuer.createSession(makeRequest());
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::DuplicateAttempt, duplicate.status);
	EXPECT_TRUE(duplicate.credential.empty());
	EXPECT_EQ(1u, manager.activeTokenCount());
}

TEST(GameSessionHttpIssuerTest, FailedIssuanceReleasesLoginAttemptReservation) {
	LoginSessionManager manager;
	int issueCalls = 0;
	auto dependencies = makeDependencies(manager);
	dependencies.issueToken = [&manager, &issueCalls](const LoginSessionIssueParams &params) -> std::optional<std::string> {
		++issueCalls;
		if (issueCalls == 1) {
			return std::nullopt;
		}
		return manager.issueToken(params);
	};
	GameSessionHttpIssuer issuer(makeConfig(), std::move(dependencies));

	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::IssueFailed, issuer.createSession(makeRequest()).status);
	const auto retried = issuer.createSession(makeRequest());
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, retried.status);
	EXPECT_EQ(2, issueCalls);
}

TEST(GameSessionHttpIssuerTest, ExpiredLoginAttemptReservationAllowsFreshIssuance) {
	LoginSessionManager manager;
	auto dependencies = makeDependencies(manager);
	auto now = FixedNow;
	dependencies.now = [&now] {
		return now;
	};
	GameSessionHttpIssuer issuer(makeConfig(), std::move(dependencies));

	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, issuer.createSession(makeRequest()).status);
	now += LoginSessionManager::DefaultTtl + std::chrono::seconds(1);
	EXPECT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, issuer.createSession(makeRequest()).status);
}

TEST(GameSessionHttpIssuerTest, WrongCharacterBurnsIssuedCredential) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager));

	const auto result = issuer.createSession(makeRequest());
	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, result.status);
	EXPECT_FALSE(manager.consumeToken(result.credential, "Sorcerer", ProtocolProfileId::Current).ok);
	EXPECT_FALSE(manager.consumeToken(result.credential, "Knight", ProtocolProfileId::Current).ok);
}

TEST(GameSessionHttpIssuerTest, WrongProfileBurnsIssuedCredential) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager));

	const auto result = issuer.createSession(makeRequest());
	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, result.status);
	EXPECT_FALSE(manager.consumeToken(result.credential, "Knight", ProtocolProfileId::Tibia1100).ok);
	EXPECT_FALSE(manager.consumeToken(result.credential, "Knight", ProtocolProfileId::Current).ok);
}

TEST(GameSessionHttpIssuerTest, ReplayOfIssuedCredentialFails) {
	LoginSessionManager manager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager));

	const auto result = issuer.createSession(makeRequest());
	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, result.status);
	ASSERT_TRUE(manager.consumeToken(result.credential, "Knight", ProtocolProfileId::Current).ok);
	EXPECT_FALSE(manager.consumeToken(result.credential, "Knight", ProtocolProfileId::Current).ok);
}

TEST(GameSessionHttpIssuerTest, ExpiredIssuedCredentialFails) {
	LoginSessionManager manager(std::chrono::seconds(0));
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(manager));

	const auto result = issuer.createSession(makeRequest());
	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, result.status);
	EXPECT_FALSE(manager.consumeToken(result.credential, "Knight", ProtocolProfileId::Current).ok);
}

TEST(GameSessionHttpIssuerTest, ProcessRestartInvalidatesProcessLocalCredential) {
	LoginSessionManager issuingManager;
	GameSessionHttpIssuer issuer(makeConfig(), makeDependencies(issuingManager));

	const auto result = issuer.createSession(makeRequest());
	ASSERT_EQ(GameSessionHttpIssuer::CreateStatus::Ok, result.status);

	LoginSessionManager restartedProcessManager;
	EXPECT_FALSE(restartedProcessManager.consumeToken(result.credential, "Knight", ProtocolProfileId::Current).ok);
}
