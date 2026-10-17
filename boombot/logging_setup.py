"""Configuración de logging: consola + archivo rotativo, con redacción de secretos."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from logging.handlers import RotatingFileHandler
from pathlib import Path

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MARK = "_boombot_handler"


class RedactingFormatter(logging.Formatter):
    """Formatter que sustituye cualquier secreto por [REDACTED] (defensa en profundidad)."""

    def __init__(self, *args: object, secrets: Iterable[str] = (), **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self._secrets = tuple(s for s in secrets if s)

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        for secret in self._secrets:
            text = text.replace(secret, "[REDACTED]")
        return text


class _IgnoreVoiceNotices(logging.Filter):
    """Oculta los avisos de 'voz no soportada' de discord.py: este bot no usa voz."""

    def filter(self, record: logging.LogRecord) -> bool:
        return "voice will NOT be supported" not in record.getMessage()


def configure_logging(level: str, log_dir: Path, secrets: Iterable[str] = ()) -> None:
    """Configura el logger raíz. Es seguro llamarla más de una vez."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(numeric_level)

    for handler in list(root.handlers):
        if getattr(handler, _MARK, False):
            root.removeHandler(handler)

    formatter = RedactingFormatter(_FORMAT, _DATE_FORMAT, secrets=tuple(secrets))

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    setattr(console, _MARK, True)
    root.addHandler(console)

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        # Tamaños contenidos (1 MB x 3) para no agotar el disco en hosting gratuito.
        file_handler = RotatingFileHandler(
            log_dir / "bot.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        setattr(file_handler, _MARK, True)
        root.addHandler(file_handler)
    except OSError as exc:  # p. ej. sistema de archivos de solo lectura
        root.warning("No se pudo escribir en %s (%s). Se registrará solo en consola.", log_dir, exc)

    # discord.py es muy verboso en DEBUG: lo limitamos a INFO como mínimo.
    logging.getLogger("discord").setLevel(max(numeric_level, logging.INFO))

    client_logger = logging.getLogger("discord.client")
    if not any(isinstance(f, _IgnoreVoiceNotices) for f in client_logger.filters):
        client_logger.addFilter(_IgnoreVoiceNotices())
