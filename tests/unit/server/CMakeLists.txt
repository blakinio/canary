target_sources(
    canary_ut
    PRIVATE network/message/networkmessage_test.cpp
            network/protocol/connection_protocol_release_gate_test.cpp
            network/protocol/multiprotocol_test.cpp
            network/protocol/protocolgame_leave_game_test.cpp
            network/protocol/transport_codec_test.cpp
)

if(UNIX
   AND DEFINED ENV{GITHUB_ACTIONS}
)
    set_property(
        TARGET canary_ut
        PROPERTY
            CXX_COMPILER_LAUNCHER
            bash
            ${CMAKE_SOURCE_DIR}/tests/unit/server/network/protocol/capture_compiler_stderr.sh
    )
endif()
