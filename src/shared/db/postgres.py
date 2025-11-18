"""Piccolo ORM client helpers for PostgreSQL access."""

from __future__ import annotations

import ssl
from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping, Optional, Sequence
from urllib.parse import quote_plus

from piccolo.engine.postgres import PostgresEngine

from src.shared.config.env import (
    MissingEnvironmentVariable,
    optional_env,
    require_env,
    require_int_env,
)


@dataclass(slots=True)
class PGConfig:
    """Piccolo."""

    name: str
    user: str
    password: str
    host: str = field(default="127.0.0.1")
    port: int = field(default=5432)
    sslmode: str = field(default="disable")
    channel_binding: str = field(default="disable")
    read_timeout: int = field(default=30)

    @classmethod
    def from_env(cls, prefix: str = "PG") -> "PGConfig":
        prefix = (prefix or "PG").strip().upper() or "PG"

        def _key(name: str) -> str:
            return f"{prefix}_{name}"

        required_specs = [
            ("name", "NAME", require_env),
            ("user", "USER", require_env),
            ("password", "PASSWORD", require_env),
            ("host", "HOST", require_env),
            ("port", "PORT", require_int_env),
            ("sslmode", "SSLMODE", require_env),
            ("read_timeout", "READ_TIMEOUT", require_int_env),
        ]
        values: dict[str, Any] = {}
        missing: list[str] = []

        for field_name, env_suffix, getter in required_specs:
            env_name = _key(env_suffix)
            try:
                values[field_name] = getter(env_name)
            except MissingEnvironmentVariable:
                missing.append(env_name)

        if missing:
            raise RuntimeError(
                "Missing required Postgres environment variables: "
                + ", ".join(missing)
            )

        channel_binding = optional_env(_key("CHANNEL_BINDING")) or "disable"

        return cls(
            name=str(values["name"]),
            user=str(values["user"]),
            password=str(values["password"]),
            host=str(values["host"]),
            port=int(values["port"]),
            sslmode=str(values["sslmode"]),
            channel_binding=channel_binding,
            read_timeout=int(values["read_timeout"]),
        )

    def _needs_dsn(self) -> bool:
        return (
            self.sslmode.lower() == "require"
            and self.channel_binding.lower() == "require"
        )

    def _build_dsn(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)
        query: list[str] = []
        if self.sslmode:
            query.append(f"sslmode={self.sslmode}")
        if self.channel_binding:
            query.append(f"channel_binding={self.channel_binding}")
        query_string = f"?{'&'.join(query)}" if query else ""
        return (
            f"postgres://{user}:{password}@{self.host}:{self.port}/"
            f"{self.name}{query_string}"
        )

    def _asyncpg_config(self) -> MutableMapping[str, Any]:
        config: MutableMapping[str, Any]
        if self._needs_dsn():
            config = {"dsn": self._build_dsn()}
        else:
            config = {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "password": self.password,
                "database": self.name,
            }
            if self.sslmode.lower() not in {"", "disable", "off"}:
                config["ssl"] = ssl.create_default_context()

        if self.read_timeout > 0:
            config["command_timeout"] = float(self.read_timeout)

        return config

    def new_engine(
        self,
        *,
        extensions: Optional[Sequence[str]] = None,
        log_queries: bool = False,
        log_responses: bool = False,
        extra_nodes: Optional[Mapping[str, PostgresEngine]] = None,
    ) -> PostgresEngine:
        config = self._asyncpg_config()
        kwargs: dict[str, Any] = {
            "config": config,
            "log_queries": log_queries,
            "log_responses": log_responses,
        }
        if extensions is not None:
            kwargs["extensions"] = tuple(extensions)
        if extra_nodes:
            kwargs["extra_nodes"] = extra_nodes
        # Defer `PostgresEngine` creation until configuration is ready so
        # importing the module doesn't immediately open a connection.
        return PostgresEngine(**kwargs)

    def must_new(
        self,
        **engine_kwargs: Any,
    ) -> PostgresEngine:
        try:
            return self.new_engine(**engine_kwargs)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Unable to create Postgres engine") from exc


def engine_from_env(
    prefix: str = "PG",
    **engine_kwargs: Any,
) -> PostgresEngine:
    return PGConfig.from_env(prefix=prefix).new_engine(**engine_kwargs)


__all__ = ["PGConfig", "engine_from_env"]
