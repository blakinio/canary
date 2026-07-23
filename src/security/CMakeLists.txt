target_sources(
    ${CORE_TARGET_NAME}
    PRIVATE argon.cpp
            game_session_http_issuer.cpp
            login_session_manager.cpp
            rsa.cpp
            rsa_backend_mbedtls.cpp
)
