"""Carga y validación de la configuración desde variables de entorno / .env.

Reglas de seguridad:
  * El token SOLO se lee de la variable de entorno DISCORD_TOKEN (o del .env local).
  * El token no aparece en repr(), en mensajes de error ni en logs.
  * Las variables de entorno reales tienen prioridad sobre el .env (útil en hosting).
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Raíz del proyecto (carpeta que contiene "boombot/"). Independiente del cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

_TRUE = {"1", "true", "yes", "y", "si", "sí", "on"}
_FALSE = {"0", "false", "no", "n", "off"}
_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class ConfigError(Exception):
    """Configuración ausente o inválida. El mensaje nunca incluye el token."""


@dataclass(frozen=True, slots=True)
class Settings:
    token: str = field(repr=False)  # repr=False: no se filtra en logs ni tracebacks
    guild_id: int | None = None
    sync_commands: bool = True
    log_level: str = "INFO"
    log_dir: Path = PROJECT_ROOT / "logs"


def _parse_bool(name: str, raw: str | None, default: bool) -> bool:
    if raw is None or not raw.strip():
        return default
    value = raw.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ConfigError(f"{name} debe ser true o false.")


def _parse_optional_int(name: str, raw: str | None) -> int | None:
    if raw is None or not raw.strip():
        return None
    value = raw.strip()
    if not value.isdigit() or int(value) <= 0:
        raise ConfigError(f"{name} debe ser un ID numérico de Discord (solo dígitos).")
    return int(value)


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Construye Settings. Si `env` es None, carga .env y usa os.environ."""
    if env is None:
        load_dotenv(PROJECT_ROOT / ".env", override=False)
        env = os.environ

    token = env.get("DISCORD_TOKEN", "").strip()
    if not token:
        raise ConfigError(
            "Falta DISCORD_TOKEN. Define la variable de entorno o crea el archivo .env "
            "(copia .env.example). Nunca escribas el token en el código."
        )
    if any(ch.isspace() for ch in token) or token[0] in "\"'":
        raise ConfigError(
            "DISCORD_TOKEN contiene espacios o comillas. Pégalo tal cual, sin comillas."
        )

    log_level = env.get("LOG_LEVEL", "INFO").strip().upper() or "INFO"
    if log_level not in _LOG_LEVELS:
        raise ConfigError(f"LOG_LEVEL debe ser uno de: {', '.join(sorted(_LOG_LEVELS))}.")

    log_dir = Path(env.get("LOG_DIR", "logs").strip() or "logs")
    if not log_dir.is_absolute():
        log_dir = PROJECT_ROOT / log_dir

    return Settings(
        token=token,
        guild_id=_parse_optional_int("DISCORD_GUILD_ID", env.get("DISCORD_GUILD_ID")),
        sync_commands=_parse_bool("SYNC_COMMANDS", env.get("SYNC_COMMANDS"), default=True),
        log_level=log_level,
        log_dir=log_dir,
    )
