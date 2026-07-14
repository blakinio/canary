target_sources(
    canary_ut
    PRIVATE network/message/networkmessage_test.cpp
            network/protocol/connection_protocol_release_gate_test.cpp
            network/protocol/multiprotocol_test.cpp
)
