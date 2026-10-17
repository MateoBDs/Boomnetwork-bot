"""Clase principal del bot: intents mínimos, carga de módulos y manejo de errores."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from .config import Settings
from .constants import EXTENSIONS, NETWORK_NAME

log = logging.getLogger(__name__)


class BoomBot(commands.Bot):
    def __init__(self, settings: Settings) -> None:
        # Principio de mínimo privilegio: solo "guilds". Cada fase posterior activará
        # únicamente el intent que necesite (members, message_content, ...).
        intents = discord.Intents.none()
        intents.guilds = True

        super().__init__(
            command_prefix=commands.when_mentioned,  # solo comandos slash en la práctica
            intents=intents,
            help_command=None,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=False
            ),
            activity=discord.Game(name=NETWORK_NAME),
        )
        self.settings = settings
        self.started_at = datetime.now(timezone.utc)
        self.tree.error(self._on_tree_error)

    # ------------------------------------------------------------------ arranque
    async def setup_hook(self) -> None:
        await self._load_extensions()
        await self._sync_commands()

    async def _load_extensions(self) -> None:
        for name in EXTENSIONS:
            try:
                await self.load_extension(name)
                log.info("Módulo cargado: %s", name)
            except Exception:  # un módulo roto no debe tumbar todo el bot
                log.exception("No se pudo cargar el módulo %s", name)

    async def _sync_commands(self) -> None:
        if not self.settings.sync_commands:
            log.info("Sincronización de comandos desactivada (SYNC_COMMANDS=false).")
            return
        try:
            if self.settings.guild_id is not None:
                guild = discord.Object(id=self.settings.guild_id)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                log.info("Sincronizados %d comandos en el servidor de pruebas.", len(synced))
            else:
                synced = await self.tree.sync()
                log.info("Sincronizados %d comandos globales.", len(synced))
        except discord.HTTPException:
            log.exception("Falló la sincronización de comandos slash.")

    async def on_ready(self) -> None:
        assert self.user is not None
        log.info(
            "Conectado como %s (id=%s) | servidores: %d | latencia: %.0f ms",
            self.user,
            self.user.id,
            len(self.guilds),
            self.latency * 1000,
        )

    # ------------------------------------------------------------------ errores
    async def _on_tree_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"⏳ Espera {error.retry_after:.0f} s antes de usar este comando de nuevo."
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = "🚫 Me faltan permisos en este servidor para hacer eso."
        elif isinstance(error, app_commands.CheckFailure):
            message = "🚫 No tienes permiso para usar este comando."
        else:
            command = interaction.command.qualified_name if interaction.command else "?"
            log.error("Error no controlado en /%s", command, exc_info=error)
            message = "⚠️ Ocurrió un error inesperado. Se ha registrado para revisarlo."

        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            log.warning("No se pudo enviar el mensaje de error al usuario.")
