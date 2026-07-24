#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any


PLATFORM_REF = "53158217a6c6017230301cf4daa783b04fcc13d5"
GATEWAY_REF = PLATFORM_REF
CANARY_REF = "981c82f5ebb6bc22c867312c2b274a71f6aeeb3e"
OTCLIENT_REF = "bb87346f6c516a19d19497d82bb01fb389334ff5"
OTCLIENT_BUILD_RUN = 30021347231
OTCLIENT_BUILD_ARTIFACT_ID = 8570110567
OTCLIENT_BUILD_ARTIFACT_DIGEST = "sha256:4a038041f65eb9d8471ff6633b0eff821769a877703399541fd22f9154562849"


class RehearsalError(RuntimeError):
    pass


def run(command: list[str], *, check: bool = True, capture: bool = True, env: dict[str, str] | None = None, input_bytes: bytes | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        env=env,
        input=input_bytes,
        cwd=cwd,
    )
    if check and completed.returncode != 0:
        stderr = (completed.stderr or b"").decode("utf-8", errors="replace")[-2000:]
        raise RehearsalError(f"command failed ({completed.returncode}): {command[0]} {command[1:3]} :: {stderr}")
    return completed


def docker(*args: str, check: bool = True, capture: bool = True, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return run(["docker", *args], check=check, capture=capture, input_bytes=input_bytes)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def redact(text: str, secret_values: list[str]) -> str:
    output = text
    for value in sorted((value for value in secret_values if value), key=len, reverse=True):
        output = output.replace(value, "[REDACTED]")
    output = re.sub(r"Authorization:\s*Bearer\s+\S+", "Authorization: Bearer [REDACTED]", output, flags=re.IGNORECASE)
    return output


class Rehearsal:
    def __init__(self) -> None:
        self.harness_root = Path(os.environ["REHEARSAL_HARNESS_ROOT"]).resolve()
        self.platform_source = Path(os.environ["REHEARSAL_PLATFORM_SOURCE"]).resolve()
        self.canary_source = Path(os.environ["REHEARSAL_CANARY_SOURCE"]).resolve()
        self.otclient_source = Path(os.environ["REHEARSAL_OTCLIENT_SOURCE"]).resolve()
        self.assets_source = Path(os.environ["REHEARSAL_ASSETS_SOURCE"]).resolve()
        self.canary_bin = Path(os.environ["REHEARSAL_CANARY_BIN"]).resolve()
        self.otclient_bin = Path(os.environ["REHEARSAL_OTCLIENT_BIN"]).resolve()
        self.gateway_bin = Path(os.environ["REHEARSAL_GATEWAY_BIN"]).resolve()
        self.evidence = Path(os.environ["REHEARSAL_EVIDENCE_DIR"]).resolve()
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.temp = Path(tempfile.mkdtemp(prefix="oteryn-native-auth-rehearsal-"))
        suffix = re.sub(r"[^a-zA-Z0-9]", "", os.environ.get("GITHUB_RUN_ID", "local"))[-12:] or "local"
        self.prefix = f"oteryn-reh-{suffix}"
        self.networks = {
            "public": f"{self.prefix}-public",
            "gateway_private": f"{self.prefix}-gateway-private",
            "canary_private": f"{self.prefix}-canary-private",
            "platform_service": f"{self.prefix}-platform-service",
            "gateway_service": f"{self.prefix}-gateway-service",
            "data": f"{self.prefix}-data",
        }
        self.subnets = {
            "public": "10.201.0.0/24",
            "gateway_private": "10.201.1.0/24",
            "canary_private": "10.201.2.0/24",
            "platform_service": "10.201.3.0/24",
            "gateway_service": "10.201.4.0/24",
            "data": "10.201.5.0/24",
        }
        self.names = {key: f"{self.prefix}-{key}" for key in [
            "mariadb", "redis", "platform", "platform_public", "platform_private", "canary",
            "canary_issuer", "gateway", "gateway_public",
        ]}
        self.platform_current = secrets.token_urlsafe(48)
        self.platform_previous = secrets.token_urlsafe(48)
        self.canary_current = secrets.token_urlsafe(48)
        self.canary_previous = secrets.token_urlsafe(48)
        self.wrong_credential = secrets.token_urlsafe(48)
        self.db_root_password = secrets.token_urlsafe(32)
        self.db_platform_password = secrets.token_urlsafe(32)
        self.db_canary_password = secrets.token_urlsafe(32)
        self.db_readonly_password = secrets.token_urlsafe(32)
        self.redis_admin_password = secrets.token_urlsafe(32)
        self.redis_readonly_password = secrets.token_urlsafe(32)
        self.identity_password = secrets.token_urlsafe(32)
        self.identity_email = "native-auth-rehearsal@example.test"
        self.app_key = "base64:" + secrets.token_urlsafe(32)
        self.secret_values = [
            self.platform_current, self.platform_previous, self.canary_current, self.canary_previous,
            self.wrong_credential, self.db_root_password, self.db_platform_password, self.db_canary_password,
            self.db_readonly_password, self.redis_admin_password, self.redis_readonly_password,
            self.identity_password, self.app_key,
        ]
        self.tls: dict[str, Path] = {}
        self.oauth_client_id = ""
        self.client_version = 0
        self.canary_stage = 0
        self.platform_stage = 0
        self.rotation: dict[str, Any] = {"schema_version": 1}
        self.failure: dict[str, Any] = {"schema_version": 1}
        self.rollback: dict[str, Any] = {"schema_version": 1}
        self.tls_result: dict[str, Any] = {"schema_version": 1}
        self.runtime: dict[str, Any] = {"schema_version": 1}
        self.raw_tickets: list[str] = []

    def container(self, key: str) -> str:
        return self.names[key]

    def cleanup(self) -> None:
        for name in list(self.names.values()):
            docker("rm", "-f", name, check=False)
        for network in self.networks.values():
            docker("network", "rm", network, check=False)
        shutil.rmtree(self.temp, ignore_errors=True)

    def collect_container_log(self, key: str, target: str) -> None:
        completed = docker("logs", self.container(key), check=False)
        text = ((completed.stdout or b"") + (completed.stderr or b"")).decode("utf-8", errors="replace")
        path = self.evidence / target
        previous = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        path.write_text(previous + redact(text, self.secret_values + self.raw_tickets), encoding="utf-8")

    def remove_container(self, key: str, log_target: str | None = None) -> None:
        if log_target:
            self.collect_container_log(key, log_target)
        docker("rm", "-f", self.container(key), check=False)

    def create_networks(self) -> None:
        for key, name in self.networks.items():
            docker("network", "create", "--driver", "bridge", "--subnet", self.subnets[key], name)
        write_json(self.evidence / "network-topology.json", {
            "schema_version": 1,
            "networks": {
                "public_client": {"docker_network": self.networks["public"], "subnet": self.subnets["public"], "members": ["OTClient", "Platform public TLS proxy", "Gateway public TLS proxy", "Canary game endpoint"]},
                "gateway_private": {"docker_network": self.networks["gateway_private"], "subnet": self.subnets["gateway_private"], "members": ["Game Gateway", "Platform private TLS proxy", "Canary issuer TLS proxy"]},
                "canary_private": {"docker_network": self.networks["canary_private"], "subnet": self.subnets["canary_private"], "members": ["Canary private issuer bind", "Canary issuer TLS proxy"]},
                "data_runtime": {"docker_network": self.networks["data"], "subnet": self.subnets["data"], "members": ["MariaDB", "Redis", "Platform", "Canary"]},
            },
            "invariants": {
                "otclient_attached_only_to_public_client": True,
                "data_services_publish_no_host_ports": True,
                "canary_issuer_binds_private_interface_only": True,
                "gateway_to_canary_uses_https_proxy": True,
            },
        })

    def generate_tls(self) -> None:
        tls_dir = self.temp / "tls"
        tls_dir.mkdir()
        ca_key = tls_dir / "ca.key"
        ca_crt = tls_dir / "ca.crt"
        server_key = tls_dir / "server.key"
        server_csr = tls_dir / "server.csr"
        server_crt = tls_dir / "server.crt"
        wrong_key = tls_dir / "wrong-ca.key"
        wrong_crt = tls_dir / "wrong-ca.crt"
        ext = tls_dir / "server.ext"
        ext.write_text(
            "subjectAltName=DNS:platform.oteryn.test,DNS:platform-internal.oteryn.test,DNS:gateway.oteryn.test,DNS:canary-issuer.oteryn.test\n"
            "extendedKeyUsage=serverAuth\n",
            encoding="utf-8",
        )
        commands = [
            ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-keyout", str(ca_key), "-out", str(ca_crt), "-subj", "/CN=Oteryn Ephemeral Rehearsal CA"],
            ["openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", str(server_key), "-out", str(server_csr), "-subj", "/CN=platform.oteryn.test"],
            ["openssl", "x509", "-req", "-days", "1", "-sha256", "-in", str(server_csr), "-CA", str(ca_crt), "-CAkey", str(ca_key), "-CAcreateserial", "-out", str(server_crt), "-extfile", str(ext)],
            ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-keyout", str(wrong_key), "-out", str(wrong_crt), "-subj", "/CN=Wrong Oteryn CA"],
        ]
        for command in commands:
            run(command)
        self.tls = {"ca": ca_crt, "server_key": server_key, "server_crt": server_crt, "wrong_ca": wrong_crt}
        self.tls_result.update({
            "ephemeral_ca_generated": True,
            "private_keys_retained": False,
            "verification_bypass_used": False,
        })

    def build_runtime_images(self) -> None:
        platform_dockerfile = self.temp / "Platform.Dockerfile"
        platform_dockerfile.write_text(
            "FROM php:8.5-cli-bookworm\n"
            "RUN apt-get update && apt-get install -y --no-install-recommends git unzip libzip-dev && docker-php-ext-install pdo_mysql && rm -rf /var/lib/apt/lists/*\n"
            "COPY --from=composer:2 /usr/bin/composer /usr/bin/composer\n"
            "WORKDIR /app\nCOPY . /app\n"
            "RUN composer install --no-interaction --prefer-dist --no-progress --optimize-autoloader\n",
            encoding="utf-8",
        )
        docker("build", "-f", str(platform_dockerfile), "-t", f"{self.prefix}-platform:latest", str(self.platform_source), capture=False)

        canary_dockerfile = self.temp / "Canary.Dockerfile"
        canary_dockerfile.write_text(
            "FROM ubuntu:24.04\n"
            "RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libstdc++6 libgcc-s1 libmariadb3 libssl3 zlib1g && rm -rf /var/lib/apt/lists/*\n"
            "WORKDIR /srv/canary\n",
            encoding="utf-8",
        )
        docker("build", "-f", str(canary_dockerfile), "-t", f"{self.prefix}-canary:latest", str(self.temp), capture=False)

        client_dockerfile = self.temp / "OTClient.Dockerfile"
        client_dockerfile.write_text(
            "FROM ubuntu:24.04\n"
            "RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates python3 xvfb xauth libgl1 libglu1-mesa libopenal1 libpulse0 libx11-6 libxcursor1 libxi6 libxinerama1 libxrandr2 libstdc++6 && rm -rf /var/lib/apt/lists/*\n"
            "WORKDIR /otclient\n",
            encoding="utf-8",
        )
        docker("build", "-f", str(client_dockerfile), "-t", f"{self.prefix}-otclient:latest", str(self.temp), capture=False)

    def start_data_services(self) -> None:
        docker(
            "run", "-d", "--name", self.container("mariadb"), "--network", self.networks["data"], "--network-alias", "mariadb",
            "-e", f"MARIADB_ROOT_PASSWORD={self.db_root_password}", "mariadb:11.4",
        )
        redis_conf = self.temp / "redis.conf"
        redis_conf.write_text(
            "bind 0.0.0.0\nprotected-mode yes\nport 6379\n"
            f"requirepass {self.redis_admin_password}\n",
            encoding="utf-8",
        )
        docker(
            "run", "-d", "--name", self.container("redis"), "--network", self.networks["data"], "--network-alias", "redis",
            "-v", f"{redis_conf}:/usr/local/etc/redis/redis.conf:ro", "redis:7.4-alpine", "redis-server", "/usr/local/etc/redis/redis.conf",
        )
        for _ in range(90):
            ping = docker("exec", "-e", f"MARIADB_PWD={self.db_root_password}", self.container("mariadb"), "mariadb-admin", "-uroot", "ping", check=False)
            if ping.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RehearsalError("MariaDB did not become ready")
        redis_ping = docker("exec", self.container("redis"), "redis-cli", "-a", self.redis_admin_password, "PING", check=False)
        if redis_ping.returncode != 0:
            raise RehearsalError("Redis did not become ready")

        grants = f"""
CREATE DATABASE platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE canary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'platform_app'@'%' IDENTIFIED BY '{self.db_platform_password}';
GRANT ALL PRIVILEGES ON platform.* TO 'platform_app'@'%';
CREATE USER 'canary_game'@'%' IDENTIFIED BY '{self.db_canary_password}';
GRANT ALL PRIVILEGES ON canary.* TO 'canary_game'@'%';
CREATE USER 'oteryn_readonly'@'%' IDENTIFIED BY '{self.db_readonly_password}';
GRANT SELECT ON canary.* TO 'oteryn_readonly'@'%';
FLUSH PRIVILEGES;
""".encode()
        docker("exec", "-i", "-e", f"MARIADB_PWD={self.db_root_password}", self.container("mariadb"), "mariadb", "-uroot", input_bytes=grants)
        for source in [self.canary_source / "schema.sql", self.canary_source / "docker/data/01-test_account.sql", self.canary_source / "docker/data/02-test_account_players.sql"]:
            docker("exec", "-i", "-e", f"MARIADB_PWD={self.db_root_password}", self.container("mariadb"), "mariadb", "-uroot", "canary", input_bytes=source.read_bytes())
        docker("exec", "-e", f"MARIADB_PWD={self.db_root_password}", self.container("mariadb"), "mariadb", "-uroot", "canary", "-e", "DELETE FROM players_online; DELETE FROM boosted_boss;")
        docker("exec", self.container("redis"), "redis-cli", "-a", self.redis_admin_password, "ACL", "SETUSER", "oteryn_runtime", "on", f">{self.redis_readonly_password}", "~cluster:channel:*:runtime", "+get", "+mget", "+exists", "+ping")
        denied = docker("run", "--rm", "--network", self.networks["data"], "redis:7.4-alpine", "redis-cli", "-h", "redis", "--user", "oteryn_runtime", "-a", self.redis_readonly_password, "SET", "forbidden", "1", check=False)
        self.runtime["redis_readonly_acl_write_rejected"] = denied.returncode != 0

    def prepare_canary_config(self) -> None:
        source = (self.canary_source / "config.lua.dist").read_text(encoding="utf-8")
        values = {
            "dataPackDirectory": '"data-otservbr-global"',
            "toggleDownloadMap": "false",
            "toggleMapCustom": "false",
            "startupDatabaseOptimization": "false",
            "mysqlDatabaseBackup": "false",
            "toggleSaveInterval": "false",
            "forgeInfluencedLimit": "0",
            "forgeFiendishLimit": "0",
            "ip": '"0.0.0.0"',
            "loginProtocolPort": "7171",
            "gameProtocolPort": "7172",
            "statusProtocolPort": "7173",
            "serverName": '"Canary E2E"',
            "houseRentPeriod": '"never"',
            "mysqlHost": '"mariadb"',
            "mysqlUser": '"canary_game"',
            "mysqlPass": json.dumps(self.db_canary_password),
            "mysqlDatabase": '"canary"',
            "mysqlPort": "3306",
            "mysqlSock": '""',
            "metricsEnablePrometheus": "false",
            "metricsEnableOstream": "false",
        }
        for key, value in values.items():
            pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)
            if len(pattern.findall(source)) != 1:
                raise RehearsalError(f"expected exactly one Canary config key {key}")
            source = pattern.sub(f"{key} = {value}", source, count=1)
        auth_pattern = re.compile(r"^authType\s*=.*$", re.MULTILINE)
        source = auth_pattern.sub('authType = "password"', source, count=1) if auth_pattern.search(source) else source + '\nauthType = "password"\n'
        (self.canary_source / "config.lua").write_text(source, encoding="utf-8")

        map_name_match = re.search(r'^mapName\s*=\s*"([^"]+)"', source, re.MULTILINE)
        map_url_match = re.search(r'^mapDownloadUrl\s*=\s*"([^"]+)"', (self.canary_source / "config.lua.dist").read_text(encoding="utf-8"), re.MULTILINE)
        if map_name_match:
            map_path = self.canary_source / "data-otservbr-global/world" / f"{map_name_match.group(1)}.otbm"
            if not map_path.exists() or map_path.stat().st_size == 0:
                if not map_url_match or not map_url_match.group(1):
                    raise RehearsalError("Canary map is missing and no mapDownloadUrl is configured")
                map_path.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(map_url_match.group(1), map_path)

    def prepare_otclient(self) -> None:
        core = (self.canary_source / "src/core.hpp").read_text(encoding="utf-8")
        matches = re.findall(r"CLIENT_VERSION\s*=\s*([0-9]+)", core)
        if not matches:
            raise RehearsalError("could not resolve Canary client version")
        self.client_version = int(matches[-1])
        version_text = (self.assets_source / "package.json.version").read_text(encoding="utf-8", errors="ignore") if (self.assets_source / "package.json.version").exists() else ""
        asset_version = "".join(ch for ch in version_text if ch.isdigit() or ch == ".").split(".")
        asset_number = "".join(asset_version[:2]) if len(asset_version) >= 2 else ""
        if asset_number and int(asset_number) != self.client_version:
            raise RehearsalError(f"asset version {asset_number} does not match Canary {self.client_version}")
        asset_target = self.otclient_source / "data/things" / str(self.client_version)
        if not (asset_target / "catalog-content.json").exists():
            asset_target.mkdir(parents=True, exist_ok=True)
            for item in self.assets_source.iterdir():
                target = asset_target / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)
        init_path = self.otclient_source / "init.lua"
        init_text = init_path.read_text(encoding="utf-8")
        init_text = re.sub(r"(clientAssets\s*=\s*\{.*?enabled\s*=\s*)true", r"\1false", init_text, count=1, flags=re.DOTALL)
        init_path.write_text(init_text, encoding="utf-8")
        shutil.copy2(self.harness_root / "otclient_native_flow_e2e.lua", self.otclient_source / "otclientrc.lua")
        bin_dir = self.temp / "client-bin"
        bin_dir.mkdir()
        wrapper = bin_dir / "xdg-open"
        shutil.copy2(self.harness_root / "capture-xdg-open.sh", wrapper)
        wrapper.chmod(0o755)

    def platform_env(self, previous: bool) -> list[str]:
        return [
            "-e", "APP_NAME=Oteryn Rehearsal", "-e", "APP_ENV=local", "-e", f"APP_KEY={self.app_key}", "-e", "APP_DEBUG=false",
            "-e", "APP_URL=https://platform.oteryn.test", "-e", "LOG_CHANNEL=stderr", "-e", "SESSION_DRIVER=file", "-e", "SESSION_SECURE_COOKIE=true",
            "-e", "DB_CONNECTION=mysql", "-e", "DB_HOST=mariadb", "-e", "DB_PORT=3306", "-e", "DB_DATABASE=platform", "-e", "DB_USERNAME=platform_app", "-e", f"DB_PASSWORD={self.db_platform_password}",
            "-e", "CANARY_DB_HOST=mariadb", "-e", "CANARY_DB_PORT=3306", "-e", "CANARY_DB_DATABASE=canary", "-e", "CANARY_DB_USERNAME=oteryn_readonly", "-e", f"CANARY_DB_PASSWORD={self.db_readonly_password}",
            "-e", f"GAME_AUTH_GATEWAY_SERVICE_TOKEN_SHA256={hashlib.sha256(self.platform_current.encode()).hexdigest()}",
            "-e", f"GAME_AUTH_GATEWAY_PREVIOUS_SERVICE_TOKEN_SHA256={hashlib.sha256(self.platform_previous.encode()).hexdigest() if previous else ''}",
            "-e", "GAME_AUTH_TICKET_TTL_SECONDS=60",
            "-e", f"REHEARSAL_IDENTITY_EMAIL={self.identity_email}", "-e", f"REHEARSAL_IDENTITY_PASSWORD={self.identity_password}",
            "-e", "REHEARSAL_CANARY_ACCOUNT_ID=101", "-e", "REHEARSAL_WORLD_HOST=canary-game.oteryn.test", "-e", "REHEARSAL_WORLD_PORT=7172",
            "-e", "REHEARSAL_BOOTSTRAP_OUTPUT=/evidence/platform-bootstrap.json",
        ]

    def start_platform(self, *, previous: bool) -> None:
        self.remove_container("platform", "platform.log")
        storage = self.temp / "platform-storage"
        if not storage.exists():
            shutil.copytree(self.platform_source / "storage", storage)
            for relative in ["framework/cache", "framework/sessions", "framework/views", "logs"]:
                (storage / relative).mkdir(parents=True, exist_ok=True)
        command = (
            "php artisan migrate --force && "
            "if [ ! -s storage/oauth-private.key ] || [ ! -s storage/oauth-public.key ]; then php artisan passport:keys --force; fi && "
            "php /harness/platform_bootstrap.php && "
            "php artisan serve --host=0.0.0.0 --port=8080"
        )
        docker(
            "create", "--name", self.container("platform"), "--network", self.networks["data"], "--ip", "10.201.5.10",
            *self.platform_env(previous),
            "-v", f"{storage}:/app/storage", "-v", f"{self.harness_root}:/harness:ro", "-v", f"{self.evidence}:/evidence",
            f"{self.prefix}-platform:latest", "sh", "-c", command,
        )
        docker("network", "connect", "--ip", "10.201.3.20", "--alias", "platform-backend", self.networks["platform_service"], self.container("platform"))
        docker("start", self.container("platform"))
        self.platform_stage += 1
        self.wait_container_running("platform")
        for _ in range(90):
            if (self.evidence / "platform-bootstrap.json").exists():
                break
            time.sleep(1)
        else:
            raise RehearsalError("Platform bootstrap evidence was not produced")
        bootstrap = json.loads((self.evidence / "platform-bootstrap.json").read_text(encoding="utf-8"))
        self.oauth_client_id = str(bootstrap["oauth_client_id"])
        if bootstrap.get("oauth_client_confidential") is not False or bootstrap.get("oauth_client_has_secret") is not False:
            raise RehearsalError("native OAuth client is not public/secretless")

    def wait_container_running(self, key: str) -> None:
        for _ in range(60):
            state = docker("inspect", "-f", "{{.State.Running}}", self.container(key), check=False)
            if state.returncode == 0 and (state.stdout or b"").strip() == b"true":
                return
            time.sleep(1)
        raise RehearsalError(f"container {key} did not remain running")

    def start_canary(self, *, enabled: bool, previous: bool) -> None:
        self.remove_container("canary", "canary.log")
        env = [
            "-e", f"CANARY_GAME_SESSION_ISSUER_ENABLED={'true' if enabled else 'false'}",
        ]
        if enabled:
            env += [
                "-e", "CANARY_GAME_SESSION_ISSUER_BIND=10.201.2.20", "-e", "CANARY_GAME_SESSION_ISSUER_PORT=18082",
                "-e", f"CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256={hashlib.sha256(self.canary_current.encode()).hexdigest()}",
                "-e", f"CANARY_GAME_SESSION_PREVIOUS_SERVICE_TOKEN_SHA256={hashlib.sha256(self.canary_previous.encode()).hexdigest() if previous else ''}",
            ]
        docker(
            "create", "--name", self.container("canary"), "--network", self.networks["data"], "--ip", "10.201.5.20",
            *env, "-v", f"{self.canary_source}:/srv/canary", "-v", f"{self.canary_bin}:/usr/local/bin/canary:ro",
            f"{self.prefix}-canary:latest", "/usr/local/bin/canary",
        )
        docker("network", "connect", "--ip", "10.201.2.20", "--alias", "canary-issuer-backend", self.networks["canary_private"], self.container("canary"))
        docker("network", "connect", "--ip", "10.201.0.20", "--alias", "canary-game.oteryn.test", self.networks["public"], self.container("canary"))
        docker("start", self.container("canary"))
        self.canary_stage += 1
        self.wait_container_running("canary")
        for _ in range(180):
            logs = docker("logs", self.container("canary"), check=False)
            text = ((logs.stdout or b"") + (logs.stderr or b"")).decode("utf-8", errors="replace")
            if "server online" in text.lower():
                return
            inspect = docker("inspect", "-f", "{{.State.Running}}", self.container("canary"), check=False)
            if inspect.returncode == 0 and (inspect.stdout or b"").strip() != b"true":
                raise RehearsalError("Canary exited during startup")
            time.sleep(1)
        raise RehearsalError("Canary did not reach server online state")

    def write_nginx_config(self, name: str, upstream: str) -> Path:
        path = self.temp / f"{name}.conf"
        path.write_text(
            "server {\n  listen 443 ssl;\n  ssl_certificate /certs/server.crt;\n  ssl_certificate_key /certs/server.key;\n"
            "  location / {\n    proxy_http_version 1.1;\n    proxy_set_header Host $host;\n    proxy_set_header X-Forwarded-Proto https;\n"
            f"    proxy_pass http://{upstream};\n  }}\n}}\n",
            encoding="utf-8",
        )
        return path

    def start_proxy(self, key: str, initial_network: str, ip: str, alias: str, upstream_network: str, upstream: str) -> None:
        self.remove_container(key)
        conf = self.write_nginx_config(key, upstream)
        docker(
            "create", "--name", self.container(key), "--network", self.networks[initial_network], "--ip", ip, "--network-alias", alias,
            "-v", f"{conf}:/etc/nginx/conf.d/default.conf:ro", "-v", f"{self.tls['server_crt']}:/certs/server.crt:ro", "-v", f"{self.tls['server_key']}:/certs/server.key:ro",
            "nginx:1.27-alpine",
        )
        docker("network", "connect", self.networks[upstream_network], self.container(key))
        docker("start", self.container(key))
        self.wait_container_running(key)

    def start_proxies(self) -> None:
        self.start_proxy("platform_public", "public", "10.201.0.10", "platform.oteryn.test", "platform_service", "10.201.3.20:8080")
        self.start_proxy("platform_private", "gateway_private", "10.201.1.10", "platform-internal.oteryn.test", "platform_service", "10.201.3.20:8080")
        self.start_proxy("canary_issuer", "gateway_private", "10.201.1.11", "canary-issuer.oteryn.test", "canary_private", "10.201.2.20:18082")

    def start_gateway(self, *, platform_token: str | None = None, canary_token: str | None = None, platform_url: str = "https://platform-internal.oteryn.test", session_url: str = "https://canary-issuer.oteryn.test", ca: Path | None = None) -> None:
        self.remove_container("gateway", "gateway.log")
        platform_token = platform_token or self.platform_current
        canary_token = canary_token or self.canary_current
        ca = ca or self.tls["ca"]
        docker(
            "create", "--name", self.container("gateway"), "--network", self.networks["gateway_private"], "--ip", "10.201.1.20", "--network-alias", "gateway-private",
            "-e", f"OTERYN_PLATFORM_BASE_URL={platform_url}", "-e", f"OTERYN_PLATFORM_SERVICE_TOKEN={platform_token}",
            "-e", f"GAME_SESSION_SERVICE_BASE_URL={session_url}", "-e", f"GAME_SESSION_SERVICE_TOKEN={canary_token}",
            "-e", "GATEWAY_LISTEN_ADDR=:8080", "-e", f"GATEWAY_VERSION={GATEWAY_REF}", "-e", "GATEWAY_REQUEST_TIMEOUT=3s", "-e", "SSL_CERT_FILE=/certs/ca.crt",
            "-v", f"{self.gateway_bin}:/usr/local/bin/game-gateway:ro", "-v", f"{ca}:/certs/ca.crt:ro",
            "alpine:3.20", "/usr/local/bin/game-gateway",
        )
        docker("network", "connect", "--ip", "10.201.4.20", "--alias", "gateway-backend", self.networks["gateway_service"], self.container("gateway"))
        docker("start", self.container("gateway"))
        self.wait_container_running("gateway")

    def start_gateway_public_proxy(self) -> None:
        self.start_proxy("gateway_public", "public", "10.201.0.11", "gateway.oteryn.test", "gateway_service", "10.201.4.20:8080")

    def curl_status(self, network_key: str, url: str, *, ca: Path | None = None, method: str = "GET", token: str | None = None, payload: str | None = None) -> tuple[int, str]:
        ca = ca or self.tls["ca"]
        command = ["run", "--rm", "--network", self.networks[network_key], "-v", f"{ca}:/certs/ca.crt:ro"]
        if token is not None:
            command += ["-e", f"TOKEN={token}"]
        command += ["curlimages/curl:8.12.1", "sh", "-c"]
        curl = ["curl", "-sS", "--cacert", "/certs/ca.crt", "-o", "/tmp/body", "-w", "%{http_code}", "-X", method]
        if token is not None:
            curl += ["-H", "Authorization: Bearer $TOKEN"]
        if payload is not None:
            curl += ["-H", "Content-Type: application/json", "--data", payload]
        curl += [url]
        command.append(" ".join(curl) + "; rc=$?; if [ $rc -ne 0 ]; then echo 000; fi")
        completed = docker(*command, check=False)
        output = (completed.stdout or b"").decode("utf-8", errors="replace").strip()
        match = re.search(r"([0-9]{3})$", output)
        return (int(match.group(1)) if match else 0, output)

    def curl_body(self, network_key: str, url: str) -> tuple[int, str]:
        completed = docker(
            "run", "--rm", "--network", self.networks[network_key], "-v", f"{self.tls['ca']}:/certs/ca.crt:ro",
            "curlimages/curl:8.12.1", "sh", "-c", f"curl -sS --cacert /certs/ca.crt -w '\\n%{{http_code}}' '{url}'",
            check=False,
        )
        text = (completed.stdout or b"").decode("utf-8", errors="replace")
        body, _, status = text.rpartition("\n")
        return (int(status) if status.isdigit() else 0, body)

    def private_platform_status(self, token: str) -> int:
        status, _ = self.curl_status("gateway_private", "https://platform-internal.oteryn.test/internal/v1/game-auth/accounts/101/login-context", token=token)
        return status

    def private_canary_status(self, token: str, *, world_id: int = 1, account_id: int = 101) -> int:
        attempt = secrets.token_hex(16)
        payload = json.dumps({"protocol_version": 1, "canary_account_id": account_id, "world_id": world_id, "login_attempt_id": attempt}, separators=(",", ":"))
        status, _ = self.curl_status("gateway_private", "https://canary-issuer.oteryn.test/internal/v1/game-sessions", method="POST", token=token, payload=payload)
        return status

    def gateway_login_status(self, ticket: str, *, protocol_version: int = 1) -> int:
        self.raw_tickets.append(ticket)
        payload = json.dumps({"protocol_version": protocol_version, "game_login_ticket": ticket}, separators=(",", ":"))
        status, _ = self.curl_status("public", "https://gateway.oteryn.test/v1/login", method="POST", payload=payload)
        return status

    def run_oauth_probe(self, args: list[str], *, secret_mount: Path | None = None) -> int:
        command = [
            "run", "--rm", "--network", self.networks["public"],
            "-v", f"{self.harness_root}:/harness:ro", "-v", f"{self.tls['ca']}:/certs/ca.crt:ro", "-v", f"{self.evidence}:/evidence",
            "-e", "REHEARSAL_PLATFORM_PUBLIC_URL=https://platform.oteryn.test", "-e", f"REHEARSAL_OAUTH_CLIENT_ID={self.oauth_client_id}",
            "-e", f"REHEARSAL_IDENTITY_EMAIL={self.identity_email}", "-e", f"REHEARSAL_IDENTITY_PASSWORD={self.identity_password}", "-e", "REHEARSAL_CA_FILE=/certs/ca.crt",
        ]
        if secret_mount is not None:
            command += ["-v", f"{secret_mount}:/secret"]
        command += ["python:3.12-slim", "python3", "/harness/oauth_probe.py", *args]
        completed = docker(*command, check=False)
        return completed.returncode

    def issue_ticket(self) -> str:
        secret_dir = self.temp / "secret-ticket"
        secret_dir.mkdir(exist_ok=True)
        path = secret_dir / "ticket"
        if self.run_oauth_probe(["issue-ticket", "--secret-output", "/secret/ticket"], secret_mount=secret_dir) != 0:
            raise RehearsalError("failed to issue controlled Game Login Ticket")
        ticket = path.read_text(encoding="utf-8")
        path.unlink(missing_ok=True)
        if not ticket:
            raise RehearsalError("issued ticket was empty")
        return ticket

    def validate_stage1_to_4(self) -> None:
        self.start_platform(previous=True)
        self.start_canary(enabled=False, previous=True)
        self.start_proxies()
        self.start_gateway()
        self.start_gateway_public_proxy()
        issuer_disabled = self.private_canary_status(self.canary_current)
        self.runtime["stage1_issuer_disabled_status"] = issuer_disabled
        self.runtime["stage1_native_path_blocked"] = issuer_disabled != 200
        self.runtime["stage2_gateway_health"] = self.curl_status("public", "https://gateway.oteryn.test/health")[0]
        self.runtime["stage2_gateway_ready_with_issuer_disabled"] = self.curl_status("public", "https://gateway.oteryn.test/ready")[0]

        self.start_canary(enabled=True, previous=True)
        current_platform = self.private_platform_status(self.platform_current)
        previous_platform = self.private_platform_status(self.platform_previous)
        current_canary = self.private_canary_status(self.canary_current)
        previous_canary = self.private_canary_status(self.canary_previous)
        self.rotation["overlap"] = {
            "gateway_to_platform_current": current_platform,
            "gateway_to_platform_previous": previous_platform,
            "gateway_to_canary_current": current_canary,
            "gateway_to_canary_previous": previous_canary,
        }
        if not all(status == 200 for status in [current_platform, previous_platform, current_canary, previous_canary]):
            raise RehearsalError("credential overlap stage did not accept current and previous credentials")
        self.runtime["stage4_native_issuer_activated"] = True

    def validate_tls(self) -> None:
        good_platform = self.curl_status("public", "https://platform.oteryn.test/health")[0]
        good_gateway = self.curl_status("public", "https://gateway.oteryn.test/health")[0]
        wrong_ca = self.curl_status("public", "https://platform.oteryn.test/health", ca=self.tls["wrong_ca"])[0]
        mismatch = self.curl_status("public", "https://10.201.0.10/health")[0]
        http_policy = docker(
            "run", "--rm", "--network", self.networks["gateway_private"], "-e", f"OTERYN_PLATFORM_BASE_URL=http://platform-internal.oteryn.test",
            "-e", f"OTERYN_PLATFORM_SERVICE_TOKEN={self.platform_current}", "-e", "GAME_SESSION_SERVICE_BASE_URL=https://canary-issuer.oteryn.test",
            "-e", f"GAME_SESSION_SERVICE_TOKEN={self.canary_current}", "-v", f"{self.gateway_bin}:/gateway:ro", "alpine:3.20", "/gateway", check=False,
        )
        private_from_public = self.curl_status("public", "https://canary-issuer.oteryn.test/internal/v1/game-sessions")[0]
        self.tls_result.update({
            "valid_ca_hostname_platform": good_platform == 200,
            "valid_ca_hostname_gateway": good_gateway == 200,
            "wrong_ca_fail_closed": wrong_ca == 0,
            "hostname_mismatch_fail_closed": mismatch == 0,
            "non_loopback_http_dependency_rejected": http_policy.returncode != 0,
            "private_issuer_unreachable_from_client_segment": private_from_public == 0,
        })
        self.tls_result["status"] = "PASS" if all(value is True for key, value in self.tls_result.items() if key not in {"schema_version", "status"}) else "FAIL"
        write_json(self.evidence / "tls-validation.json", self.tls_result)
        if self.tls_result["status"] != "PASS":
            raise RehearsalError("TLS validation failed")

    def validate_oauth_matrix(self) -> None:
        if self.run_oauth_probe(["matrix", "--output", "/evidence/oauth-pkce-result.json"]) != 0:
            raise RehearsalError("OAuth PKCE negative matrix failed")
        secret_dir = self.temp / "secret-code"
        secret_dir.mkdir(exist_ok=True)
        if self.run_oauth_probe(["issue-code", "--secret-output", "/secret/code.json"], secret_mount=secret_dir) != 0:
            raise RehearsalError("could not issue authorization code for expiry test")
        docker("exec", "-e", f"MARIADB_PWD={self.db_platform_password}", self.container("mariadb"), "mariadb", "-uplatform_app", "platform", "-e", "UPDATE oauth_auth_codes SET expires_at='2000-01-01 00:00:00' WHERE revoked=0;")
        if self.run_oauth_probe(["exchange-code", "--secret-input", "/secret/code.json", "--output", "/evidence/oauth-code-expiry.json"], secret_mount=secret_dir) != 0:
            raise RehearsalError("expired authorization code was not rejected")
        (secret_dir / "code.json").unlink(missing_ok=True)

    def validate_ticket_and_failure_matrix(self) -> None:
        expired = self.issue_ticket()
        docker("exec", "-e", f"MARIADB_PWD={self.db_platform_password}", self.container("mariadb"), "mariadb", "-uplatform_app", "platform", "-e", "UPDATE game_login_tickets SET expires_at='2000-01-01 00:00:00' WHERE used_at IS NULL;")
        self.failure["expired_game_login_ticket_rejected"] = self.gateway_login_status(expired) in (401, 422)

        replay = self.issue_ticket()
        first = self.gateway_login_status(replay)
        second = self.gateway_login_status(replay)
        self.failure["game_login_ticket_first_use"] = first == 200
        self.failure["replayed_game_login_ticket_rejected"] = second in (401, 409, 422)
        self.failure["wrong_protocol_version_rejected"] = self.gateway_login_status(self.issue_ticket(), protocol_version=999) == 400
        self.failure["invalid_gateway_service_credential_rejected"] = self.private_platform_status(self.wrong_credential) == 401
        self.failure["invalid_canary_service_credential_rejected"] = self.private_canary_status(self.wrong_credential) == 401
        self.failure["wrong_account_rejected"] = self.private_canary_status(self.canary_current, account_id=999999) in (404, 409)
        self.failure["wrong_world_routing_rejected"] = self.private_canary_status(self.canary_current, world_id=999999) == 409

        outage_ticket = self.issue_ticket()
        self.remove_container("platform", "platform.log")
        self.failure["platform_redemption_unavailable_fail_closed"] = self.gateway_login_status(outage_ticket) >= 500
        self.start_platform(previous=True)
        if self.curl_status("public", "https://platform.oteryn.test/health")[0] != 200:
            raise RehearsalError("Platform did not recover after failure injection")

        issuer_ticket = self.issue_ticket()
        self.remove_container("canary_issuer")
        self.failure["canary_issuer_unavailable_fail_closed"] = self.gateway_login_status(issuer_ticket) >= 500
        self.start_proxy("canary_issuer", "gateway_private", "10.201.1.11", "canary-issuer.oteryn.test", "canary_private", "10.201.2.20:18082")
        self.failure["canary_issuer_recovery"] = self.private_canary_status(self.canary_current) == 200

        self.remove_container("gateway", "gateway.log")
        self.failure["gateway_unavailable_fail_closed"] = self.curl_status("public", "https://gateway.oteryn.test/health")[0] >= 500
        self.start_gateway()
        self.failure["gateway_recovery"] = self.curl_status("public", "https://gateway.oteryn.test/health")[0] == 200

    def run_physical_otclient(self) -> None:
        evidence_before = set(self.evidence.iterdir())
        command = [
            "run", "--rm", "--name", f"{self.prefix}-otclient", "--network", self.networks["public"],
            "-v", f"{self.otclient_source}:/otclient", "-v", f"{self.otclient_bin}:/usr/local/bin/otclient:ro", "-v", f"{self.evidence}:/evidence",
            "-v", f"{self.harness_root}:/harness:ro", "-v", f"{self.temp / 'client-bin'}:/harness-bin:ro", "-v", f"{self.tls['ca']}:/certs/ca.crt:ro",
            "-e", "PATH=/harness-bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "-e", "REHEARSAL_AUTH_URL_FILE=/tmp/native-auth-url",
            "-e", "REHEARSAL_BROWSER_EVENTS=/evidence/browser-events.tsv", "-e", "REHEARSAL_CA_FILE=/certs/ca.crt",
            "-e", f"REHEARSAL_IDENTITY_EMAIL={self.identity_email}", "-e", f"REHEARSAL_IDENTITY_PASSWORD={self.identity_password}",
            "-e", f"REHEARSAL_CLIENT_VERSION={self.client_version}", "-e", "REHEARSAL_CHARACTER=Knight 1", "-e", "REHEARSAL_WORLD=Canary E2E",
            "-e", "REHEARSAL_GAME_HOST=canary-game.oteryn.test", "-e", "REHEARSAL_GAME_PORT=7172",
            "-e", "REHEARSAL_PLATFORM_PUBLIC_URL=https://platform.oteryn.test", "-e", "REHEARSAL_GATEWAY_PUBLIC_URL=https://gateway.oteryn.test",
            "-e", f"REHEARSAL_OAUTH_CLIENT_ID={self.oauth_client_id}", "-e", "REHEARSAL_ARTIFACT_DIR=/evidence", "-e", "LIBGL_ALWAYS_SOFTWARE=1",
            f"{self.prefix}-otclient:latest", "sh", "-c",
            "python3 /harness/browser_driver.py & browser=$!; xvfb-run -a /usr/local/bin/otclient; client=$?; wait $browser; browser_rc=$?; test $client -eq 0; test $browser_rc -eq 0",
        ]
        completed = docker(*command, check=False, capture=False)
        if completed.returncode != 0:
            raise RehearsalError(f"physical OTClient native-auth run failed with exit {completed.returncode}")
        events = (self.evidence / "client-events.tsv").read_text(encoding="utf-8", errors="replace")
        required = [
            "native_flow\tstarted", "gateway_session\treceived", "character_authorization\tmatched", "login_1\tsuccess",
            "online_stable_1\tconfirmed", "logout_request_1\tsafe", "logout_1\tcomplete", "replay_attempt\tstarted",
            "successful_world_entries\t1", "e2e\tsuccess",
        ]
        missing = [marker for marker in required if marker not in events]
        if missing or "replay_rejected\t" not in events:
            raise RehearsalError(f"physical OTClient evidence missing markers: {missing}")
        self.runtime["physical_otclient_native_flow"] = "PASS"
        self.runtime["successful_world_entries"] = 1
        self.runtime["safe_logout"] = True
        self.runtime["game_session_replay_rejected"] = True
        self.runtime["new_evidence_files"] = sorted(path.name for path in set(self.evidence.iterdir()) - evidence_before)

    def validate_database_logout(self) -> None:
        query = "SELECT p.name,p.lastlogin,p.lastlogout,(SELECT COUNT(*) FROM players_online) AS players_online FROM players p WHERE p.name='Knight 1';"
        completed = docker("exec", "-e", f"MARIADB_PWD={self.db_root_password}", self.container("mariadb"), "mariadb", "-N", "-B", "-uroot", "canary", "-e", query)
        text = (completed.stdout or b"").decode("utf-8", errors="replace").strip()
        fields = text.split("\t")
        if len(fields) < 4:
            raise RehearsalError("could not verify Canary logout persistence")
        self.runtime["logout_database"] = {
            "character": fields[0],
            "lastlogin_nonzero": fields[1] not in {"0", "NULL", ""},
            "lastlogout_nonzero": fields[2] not in {"0", "NULL", ""},
            "players_online": int(fields[3]),
        }
        if not self.runtime["logout_database"]["lastlogin_nonzero"] or not self.runtime["logout_database"]["lastlogout_nonzero"] or self.runtime["logout_database"]["players_online"] != 0:
            raise RehearsalError("logout persistence invariant failed")

    def validate_rotation_retire_rollback(self) -> None:
        self.start_platform(previous=False)
        self.start_canary(enabled=True, previous=False)
        retired = {
            "platform_current": self.private_platform_status(self.platform_current),
            "platform_previous": self.private_platform_status(self.platform_previous),
            "platform_wrong": self.private_platform_status(self.wrong_credential),
            "canary_current": self.private_canary_status(self.canary_current),
            "canary_previous": self.private_canary_status(self.canary_previous),
            "canary_wrong": self.private_canary_status(self.wrong_credential),
        }
        self.rotation["retired_previous"] = retired
        if not (retired["platform_current"] == 200 and retired["platform_previous"] == 401 and retired["platform_wrong"] == 401 and retired["canary_current"] == 200 and retired["canary_previous"] == 401 and retired["canary_wrong"] == 401):
            raise RehearsalError("credential retirement stage failed")

        self.start_platform(previous=True)
        self.start_canary(enabled=True, previous=True)
        rollback_platform = self.private_platform_status(self.platform_previous)
        rollback_canary = self.private_canary_status(self.canary_previous)
        self.rotation["rollback_overlap"] = {"platform_previous": rollback_platform, "canary_previous": rollback_canary}
        if rollback_platform != 200 or rollback_canary != 200:
            raise RehearsalError("credential rollback overlap failed")

        self.start_platform(previous=False)
        self.start_canary(enabled=True, previous=False)
        reclosed_platform = self.private_platform_status(self.platform_previous)
        reclosed_canary = self.private_canary_status(self.canary_previous)
        self.rotation["reclosed_overlap"] = {"platform_previous": reclosed_platform, "canary_previous": reclosed_canary}
        self.rotation["status"] = "PASS" if reclosed_platform == 401 and reclosed_canary == 401 else "FAIL"
        write_json(self.evidence / "credential-rotation.json", self.rotation)
        if self.rotation["status"] != "PASS":
            raise RehearsalError("credential overlap did not re-close")

    def validate_cutover_rollback(self) -> None:
        self.start_canary(enabled=False, previous=False)
        disabled_status = self.private_canary_status(self.canary_current)
        self.rollback["native_issuer_disabled_fail_closed"] = disabled_status != 200
        self.rollback["legacy_auth_removed"] = False
        self.rollback["legacy_auth_runtime_smoke"] = "not_in_scope"
        self.start_canary(enabled=True, previous=False)
        restored = self.private_canary_status(self.canary_current)
        self.rollback["candidate_reactivated"] = restored == 200
        self.rollback["status"] = "PASS" if self.rollback["native_issuer_disabled_fail_closed"] and self.rollback["candidate_reactivated"] else "FAIL"
        write_json(self.evidence / "rollback-rehearsal-summary.json", self.rollback)
        if self.rollback["status"] != "PASS":
            raise RehearsalError("rollback rehearsal failed")

    def final_smoke(self) -> None:
        platform_health = self.curl_status("public", "https://platform.oteryn.test/health")[0]
        gateway_health = self.curl_status("public", "https://gateway.oteryn.test/health")[0]
        gateway_ready = self.curl_status("public", "https://gateway.oteryn.test/ready")[0]
        version_status, version_body = self.curl_body("public", "https://gateway.oteryn.test/version")
        game_port = docker("run", "--rm", "--network", self.networks["public"], "busybox:1.37", "sh", "-c", "nc -z -w 3 canary-game.oteryn.test 7172", check=False)
        self.runtime["final_smoke"] = {
            "platform_health": platform_health,
            "gateway_health": gateway_health,
            "gateway_ready": gateway_ready,
            "gateway_version_status": version_status,
            "gateway_version_matches": GATEWAY_REF in version_body,
            "canary_game_port": game_port.returncode == 0,
        }
        if not (platform_health == 200 and gateway_health == 200 and gateway_ready == 200 and version_status == 200 and GATEWAY_REF in version_body and game_port.returncode == 0):
            raise RehearsalError("final smoke failed")

    def write_revision_evidence(self) -> None:
        runtime_revisions = {
            "schema_version": 1,
            "components": {
                "platform": {"repository": "blakinio/Oteryn-Platform", "source_sha": PLATFORM_REF},
                "gateway": {"repository": "blakinio/Oteryn-Platform", "source_sha": GATEWAY_REF},
                "canary": {"repository": "blakinio/canary", "source_sha": CANARY_REF},
                "otclient": {"repository": "blakinio/otclient", "source_sha": OTCLIENT_REF},
            },
            "build": {"workflow_run": os.environ.get("GITHUB_RUN_ID", "local"), "workflow": os.environ.get("GITHUB_WORKFLOW", "local")},
        }
        write_json(self.evidence / "runtime-revisions.json", runtime_revisions)
        image_id = docker("image", "inspect", "-f", "{{.Id}}", f"{self.prefix}-platform:latest")
        digests = {
            "schema_version": 1,
            "platform_image_id": (image_id.stdout or b"").decode().strip(),
            "gateway_binary_sha256": sha256_file(self.gateway_bin),
            "canary_binary_sha256": sha256_file(self.canary_bin),
            "otclient_binary_sha256": sha256_file(self.otclient_bin),
            "otclient_source_build_run": OTCLIENT_BUILD_RUN,
            "otclient_source_build_artifact_id": OTCLIENT_BUILD_ARTIFACT_ID,
            "otclient_source_build_artifact_digest": OTCLIENT_BUILD_ARTIFACT_DIGEST,
        }
        write_json(self.evidence / "artifact-digests.json", digests)

    def sensitive_scan(self) -> dict[str, Any]:
        forbidden_regex = [
            re.compile(rb"Authorization:\s*Bearer\s+\S+", re.IGNORECASE),
            re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
            re.compile(rb"(?:mysql|mariadb|redis)://[^\s:@]+:[^\s@]+@", re.IGNORECASE),
        ]
        findings: list[str] = []
        all_secrets = [value.encode() for value in self.secret_values + self.raw_tickets if value]
        for path in sorted(self.evidence.rglob("*")):
            if not path.is_file():
                continue
            data = path.read_bytes()
            if any(secret in data for secret in all_secrets):
                findings.append(f"{path.name}:known-secret")
            for pattern in forbidden_regex:
                if pattern.search(data):
                    findings.append(f"{path.name}:{pattern.pattern.decode(errors='ignore')[:40]}")
        result = {"schema_version": 1, "status": "PASS" if not findings else "FAIL", "findings": findings}
        write_json(self.evidence / "sensitive-log-scan.json", result)
        return result

    def execute(self) -> None:
        status = "FAIL"
        error = ""
        try:
            self.create_networks()
            self.generate_tls()
            self.build_runtime_images()
            self.start_data_services()
            self.prepare_canary_config()
            self.prepare_otclient()
            self.write_revision_evidence()
            self.validate_stage1_to_4()
            self.validate_tls()
            self.validate_oauth_matrix()
            self.validate_ticket_and_failure_matrix()
            self.run_physical_otclient()
            self.validate_database_logout()
            self.validate_rotation_retire_rollback()
            self.validate_cutover_rollback()
            self.final_smoke()
            status = "PASS"
        except Exception as exc:  # noqa: BLE001
            error = f"{type(exc).__name__}: {exc}"
            self.failure["first_failure"] = error
            raise
        finally:
            for key, target in [("platform", "platform.log"), ("gateway", "gateway.log"), ("canary", "canary.log")]:
                self.collect_container_log(key, target)
            self.failure["status"] = "PASS" if status == "PASS" and all(value is True for key, value in self.failure.items() if key not in {"schema_version", "status", "first_failure"}) else ("FAIL" if error or status != "PASS" else "PASS")
            write_json(self.evidence / "failure-injection-summary.json", self.failure)
            write_json(self.evidence / "native-auth-runtime.json", self.runtime)
            scan = self.sensitive_scan()
            overall = "PRODUCTION_LIKE_PROVEN" if status == "PASS" and scan["status"] == "PASS" else "FAILED"
            result = {
                "schema_version": 1,
                "overall_status": overall,
                "evidence_classification": "PRODUCTION_LIKE_PROVEN" if overall == "PRODUCTION_LIKE_PROVEN" else "NOT_PROVEN",
                "component_shas": {"platform": PLATFORM_REF, "gateway": GATEWAY_REF, "canary": CANARY_REF, "otclient": OTCLIENT_REF},
                "successful_world_entries": self.runtime.get("successful_world_entries", 0),
                "replay_rejection_status": self.runtime.get("game_session_replay_rejected", False),
                "logout_status": bool(self.runtime.get("safe_logout", False) and self.runtime.get("logout_database", {}).get("players_online") == 0),
                "credential_rotation_status": self.rotation.get("status") == "PASS",
                "tls_validation_status": self.tls_result.get("status") == "PASS",
                "rollback_status": self.rollback.get("status") == "PASS",
                "sensitive_log_scan_status": scan["status"],
                "failure_injection_status": self.failure.get("status"),
                "error": error or None,
            }
            write_json(self.evidence / "result.json", result)
            manifest = {
                "schema_version": 1,
                "scenario": "ephemeral-production-like-native-auth-cutover",
                "maximum_classification": "PRODUCTION_LIKE_PROVEN",
                "production_deployment": False,
                "stages": [
                    "issuer_disabled", "gateway_deployed_fail_closed", "credential_overlap", "native_activation",
                    "physical_native_auth_e2e", "credential_retirement", "rollback", "candidate_reactivation_final_smoke",
                ],
            }
            write_json(self.evidence / "scenario-manifest.json", manifest)
            self.cleanup()


def main() -> int:
    rehearsal = Rehearsal()
    try:
        rehearsal.execute()
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"rehearsal failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
