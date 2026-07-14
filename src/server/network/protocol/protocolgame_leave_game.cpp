/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "server/network/protocol/protocolgame.hpp"

#include "config/configmanager.hpp"
#include "creatures/players/livestream/livestream.hpp"
#include "creatures/players/player.hpp"
#include "game/game.hpp"
#include "lua/creature/creatureevent.hpp"
#include "server/network/connection/connection.hpp"
#include "server/network/message/networkmessage.hpp"
#include "server/network/message/outputmessage.hpp"

namespace {
	[[nodiscard]] std::string_view getClientLeaveGameStateName(ClientLeaveGameState state) {
		switch (state) {
			case ClientLeaveGameState::None:
				return "none";
			case ClientLeaveGameState::Queued:
				return "queued";
			case ClientLeaveGameState::Dispatching:
				return "dispatching";
			case ClientLeaveGameState::Completed:
				return "completed";
			case ClientLeaveGameState::Denied:
				return "denied";
			case ClientLeaveGameState::Rejected:
				return "rejected";
		}

		return "unknown";
	}
}

void ProtocolGame::setClientLeaveGameState(ClientLeaveGameState state, std::string_view reason) {
	clientLeaveGameState.store(state, std::memory_order_release);

	const auto connection = getConnection();
	const auto exactPlayer = clientLeaveGamePlayer ? clientLeaveGamePlayer : player;
	g_logger().info(
		"[ProtocolGameLeaveGame] event=client_leave_state state={} reason={} connection_id={} connection={} protocol={} player={} player_guid={} player_runtime_id={} player_client={}",
		getClientLeaveGameStateName(state),
		reason,
		connection ? connection->getConnectionId() : 0,
		fmt::ptr(connection.get()),
		fmt::ptr(this),
		fmt::ptr(exactPlayer.get()),
		exactPlayer ? exactPlayer->getGUID() : 0,
		exactPlayer ? exactPlayer->getID() : 0,
		fmt::ptr(exactPlayer ? exactPlayer->client.get() : nullptr)
	);
}

bool ProtocolGame::queueClientLeaveGame() {
	ClientLeaveGameState expected = ClientLeaveGameState::None;
	if (!clientLeaveGameState.compare_exchange_strong(expected, ClientLeaveGameState::Queued, std::memory_order_acq_rel)) {
		g_logger().warn(
			"[ProtocolGameLeaveGame] event=client_leave_queue_rejected state={} protocol={}",
			getClientLeaveGameStateName(expected),
			fmt::ptr(this)
		);
		return false;
	}

	setClientLeaveGameState(ClientLeaveGameState::Queued, "validated-opcode");
	return true;
}

void ProtocolGame::dispatchClientLeaveGame(NetworkMessage &msg) {
	ClientLeaveGameState expected = ClientLeaveGameState::Queued;
	if (!clientLeaveGameState.compare_exchange_strong(expected, ClientLeaveGameState::Dispatching, std::memory_order_acq_rel)) {
		g_logger().warn(
			"[ProtocolGameLeaveGame] event=client_leave_dispatch_rejected state={} protocol={}",
			getClientLeaveGameStateName(expected),
			fmt::ptr(this)
		);
		return;
	}

	clientLeaveGamePlayer = player;
	setClientLeaveGameState(ClientLeaveGameState::Dispatching, "dispatcher-begin");

#ifdef BUILD_TESTS
	++clientLeaveParseCountForTest;
#endif

	g_logger().info(
		"[ProtocolGameLeaveGame] event=protocolgame_parse_packet_enter protocol={} player={} opcode_expected=0x14",
		fmt::ptr(this),
		fmt::ptr(clientLeaveGamePlayer.get())
	);

	if (!msg.canRead(sizeof(uint8_t))) {
		setClientLeaveGameState(ClientLeaveGameState::Rejected, "missing-opcode");
		return;
	}

	const auto opcode = msg.getByte();
	if (opcode != 0x14) {
		setClientLeaveGameState(ClientLeaveGameState::Rejected, "unexpected-opcode");
		return;
	}

	executeClientLeaveGame(clientLeaveGamePlayer, true, false);
}

bool ProtocolGame::executeClientLeaveGame(const std::shared_ptr<Player> &expectedPlayer, bool displayEffect, bool forced) {
	g_logger().info(
		"[ProtocolGameLeaveGame] event=logout_enter protocol={} expected_player={} current_player={} expected_client={} forced={}",
		fmt::ptr(this),
		fmt::ptr(expectedPlayer.get()),
		fmt::ptr(player.get()),
		fmt::ptr(expectedPlayer ? expectedPlayer->client.get() : nullptr),
		forced
	);

	if (!expectedPlayer) {
		setClientLeaveGameState(ClientLeaveGameState::Rejected, "missing-player");
		return false;
	}

	const auto self = getThis();
	if (player != expectedPlayer) {
		setClientLeaveGameState(ClientLeaveGameState::Rejected, "player-object-changed");
		return false;
	}

	if (expectedPlayer->client != self) {
		setClientLeaveGameState(ClientLeaveGameState::Rejected, "stale-protocol-identity");
		return false;
	}

	if (m_isLivestreamViewer) {
		sendSessionEndInformation(SESSION_END_LOGOUT);
		setClientLeaveGameState(ClientLeaveGameState::Completed, "livestream-viewer");
		return true;
	}

#ifdef BUILD_TESTS
	if (leaveGameDeniedForTest) {
		setClientLeaveGameState(ClientLeaveGameState::Denied, "test-denial");
		return false;
	}
#endif

	const bool removePlayer = !expectedPlayer->isRemoved() && !forced;
	const auto tile = expectedPlayer->getTile();
	if (removePlayer && !expectedPlayer->isAccessPlayer()) {
		if (tile && tile->hasFlag(TILESTATE_NOLOGOUT)) {
			expectedPlayer->sendCancelMessage(RETURNVALUE_YOUCANNOTLOGOUTHERE);
			setClientLeaveGameState(ClientLeaveGameState::Denied, "no-logout-tile");
			return false;
		}

		if (tile && !tile->hasFlag(TILESTATE_PROTECTIONZONE) && expectedPlayer->hasCondition(CONDITION_INFIGHT)) {
			expectedPlayer->sendCancelMessage(RETURNVALUE_YOUMAYNOTLOGOUTDURINGAFIGHT);
			setClientLeaveGameState(ClientLeaveGameState::Denied, "in-fight");
			return false;
		}
	}

	if (removePlayer && !g_creatureEvents().playerLogout(expectedPlayer)) {
		setClientLeaveGameState(ClientLeaveGameState::Denied, "logout-event");
		return false;
	}

	if (player != expectedPlayer || expectedPlayer->client != self) {
		setClientLeaveGameState(ClientLeaveGameState::Rejected, "identity-changed-after-logout-event");
		return false;
	}

	displayEffect = displayEffect && !expectedPlayer->isRemoved() && expectedPlayer->getHealth() > 0 && !expectedPlayer->isInGhostMode();
	if (displayEffect) {
		g_game().addMagicEffect(expectedPlayer->getPosition(), CONST_ME_POFF);
	}

	acceptPackets = false;
	clearReusableSessionHints();
	sendSessionEndInformation(forced ? SESSION_END_FORCECLOSE : SESSION_END_LOGOUT);

	bool removed = false;
#ifdef BUILD_TESTS
	if (leaveGameRemoveCreatureForTest) {
		++clientLeaveRemoveCountForTest;
		removed = leaveGameRemoveCreatureForTest(expectedPlayer);
	} else {
#endif
		removed = g_game().removeCreature(expectedPlayer, true);
#ifdef BUILD_TESTS
	}
#endif

	const bool completed = removed || expectedPlayer->isRemoved();
	g_logger().info(
		"[ProtocolGameLeaveGame] event=remove_creature_result protocol={} player={} removed_result={} player_removed={} exact_client={}",
		fmt::ptr(this),
		fmt::ptr(expectedPlayer.get()),
		removed,
		expectedPlayer->isRemoved(),
		expectedPlayer->client == self
	);

	if (!completed) {
		setClientLeaveGameState(ClientLeaveGameState::Rejected, "remove-creature-failed");
		return false;
	}

	setClientLeaveGameState(ClientLeaveGameState::Completed, "player-removed");
	return true;
}

void ProtocolGame::releaseFromConnection() {
	const auto state = clientLeaveGameState.load(std::memory_order_acquire);
	const auto exactPlayer = clientLeaveGamePlayer ? clientLeaveGamePlayer : player;
	const auto self = getThis();

	g_logger().info(
		"[ProtocolGameLeaveGame] event=release_enter state={} protocol={} player={} player_client={} exact_client={}",
		getClientLeaveGameStateName(state),
		fmt::ptr(this),
		fmt::ptr(exactPlayer.get()),
		fmt::ptr(exactPlayer ? exactPlayer->client.get() : nullptr),
		exactPlayer && exactPlayer->client == self
	);

	if (state == ClientLeaveGameState::Queued || state == ClientLeaveGameState::Dispatching) {
		g_logger().error(
			"[ProtocolGameLeaveGame] event=release_before_leave_dispatch_complete state={} protocol={} player={}",
			getClientLeaveGameStateName(state),
			fmt::ptr(this),
			fmt::ptr(exactPlayer.get())
		);
		return;
	}

	if (clientLeaveReleaseCompleted.exchange(true, std::memory_order_acq_rel)) {
		g_logger().warn(
			"[ProtocolGameLeaveGame] event=duplicate_release_ignored state={} protocol={}",
			getClientLeaveGameStateName(state),
			fmt::ptr(this)
		);
		return;
	}

#ifdef BUILD_TESTS
	++clientLeaveReleaseCountForTest;
#endif

	if (state == ClientLeaveGameState::Denied && player && player == exactPlayer && exactPlayer->client == self) {
		// A denied logout must not be converted into a detached online player.
		// Break the ProtocolGame -> Player edge while preserving Player -> exact
		// ProtocolGame so replacement-login logic can identify this exact session.
		clearReusableSessionHints();
		player = nullptr;
		clientLeaveGamePlayer = nullptr;
		OutputMessagePool::getInstance().removeProtocolFromAutosend(shared_from_this());
		Protocol::release();
	} else {
		release();
		if (state == ClientLeaveGameState::Rejected) {
			player = nullptr;
		}
		clientLeaveGamePlayer = nullptr;
	}

	g_logger().info(
		"[ProtocolGameLeaveGame] event=release_complete state={} protocol={} exact_player={} exact_player_client={}",
		getClientLeaveGameStateName(state),
		fmt::ptr(this),
		fmt::ptr(exactPlayer.get()),
		fmt::ptr(exactPlayer ? exactPlayer->client.get() : nullptr)
	);
}

#ifdef BUILD_TESTS
void ProtocolGame::attachPlayerForLeaveGameTest(const std::shared_ptr<Player> &testPlayer) {
	player = testPlayer;
	if (player) {
		player->client = getThis();
	}
	acceptPackets = true;
	loggedIn = true;
}

void ProtocolGame::setLeaveGameRemoveCreatureForTest(std::function<bool(const std::shared_ptr<Player> &)> callback) {
	leaveGameRemoveCreatureForTest = std::move(callback);
}

void ProtocolGame::setLeaveGameDeniedForTest(bool denied) {
	leaveGameDeniedForTest = denied;
}

ClientLeaveGameState ProtocolGame::getClientLeaveGameStateForTest() const {
	return clientLeaveGameState.load(std::memory_order_acquire);
}

uint32_t ProtocolGame::getClientLeaveParseCountForTest() const {
	return clientLeaveParseCountForTest.load(std::memory_order_acquire);
}

uint32_t ProtocolGame::getClientLeaveRemoveCountForTest() const {
	return clientLeaveRemoveCountForTest.load(std::memory_order_acquire);
}

uint32_t ProtocolGame::getClientLeaveReleaseCountForTest() const {
	return clientLeaveReleaseCountForTest.load(std::memory_order_acquire);
}
#endif
