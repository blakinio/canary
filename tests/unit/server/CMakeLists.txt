target_sources(
    canary_ut
    PRIVATE network/message/networkmessage_test.cpp
            network/protocol/connection_protocol_release_gate_test.cpp
            network/protocol/multiprotocol_test.cpp
            network/protocol/protocolgame_leave_game_test.cpp
            network/protocol/transport_codec_test.cpp
)
