"""Punto de entrada:  python -m boombot"""

from __future__ import annotations

import logging
import sys

import aiohttp  # dependencia obligatoria de discord.py
import discord

from . import __version__
from .bot import BoomBot
from .config import ConfigError, load_settings
from .logging_setup import configure_logging


def main() -> int:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"[configuración] {exc}", file=sys.stderr)
        return 2

    configure_logging(settings.log_level, settings.log_dir, secrets=[settings.token])
    log = logging.getLogger("boombot")
    log.info("Iniciando BoomBot v%s", __version__)

    bot = BoomBot(settings)
    try:
        # log_handler=None: el logging ya está configurado por nosotros.
        bot.run(settings.token, log_handler=None)
    except discord.LoginFailure:
        log.critical(
            "Discord rechazó el token. Genera uno nuevo en el Developer Portal "
            "(Bot -> Reset Token) y actualiza tu .env."
        )
        return 1
    except discord.PrivilegedIntentsRequired:
        log.critical("Se pidió un intent privilegiado que no está activado en el Developer Portal.")
        return 1
    except aiohttp.ClientError as exc:
        log.critical("No se pudo conectar con Discord (%s). Revisa tu conexión a Internet.", type(exc).__name__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
