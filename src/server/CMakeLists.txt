target_sources(
    ${CORE_TARGET_NAME}
    PRIVATE network/connection/connection.cpp
            network/message/networkmessage.cpp
            network/message/outputmessage.cpp
            network/protocol/protocol.cpp
            network/protocol/protocol_profile.cpp
            network/protocol/protocolgame.cpp
            network/protocol/protocolgame_leave_game.cpp
            network/protocol/protocollogin.cpp
            network/protocol/protocol_session_hint.cpp
            network/protocol/protocolstatus.cpp
            network/protocol/transport_codec.cpp
            network/webhook/webhook.cpp
            server.cpp
            signals.cpp
)

if(BUILD_TESTS AND UNIX AND DEFINED ENV{GITHUB_ACTIONS})
    set_property(
        TARGET ${CORE_TARGET_NAME}
        PROPERTY CXX_COMPILER_LAUNCHER
                 bash
                 ${CMAKE_SOURCE_DIR}/tests/unit/server/network/protocol/capture_compiler_stderr.sh
    )
endif()
