"""Módulo núcleo: comandos básicos para comprobar que el bot funciona."""

from __future__ import annotations

import math
import platform
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from .. import __version__
from ..constants import GAME_MODES, NETWORK_NAME, RANKS
from ..utils.embeds import brand_embed

if TYPE_CHECKING:
    from ..bot import BoomBot


class Core(commands.Cog):
    def __init__(self, bot: BoomBot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Comprueba que el bot responde y su latencia.")
    @app_commands.checks.cooldown(1, 5.0)
    async def ping(self, interaction: discord.Interaction) -> None:
        latency = self.bot.latency
        text = "n/d" if math.isnan(latency) or math.isinf(latency) else f"{round(latency * 1000)} ms"
        await interaction.response.send_message(f"🏓 ¡Pong! Latencia: **{text}**", ephemeral=True)

    @app_commands.command(name="info", description=f"Información sobre el bot de {NETWORK_NAME}.")
    @app_commands.checks.cooldown(1, 10.0)
    async def info(self, interaction: discord.Interaction) -> None:
        embed = brand_embed(f"{NETWORK_NAME} · Bot", "Bot oficial de la network.")
        embed.add_field(name="Versión", value=__version__)
        embed.add_field(name="Encendido", value=discord.utils.format_dt(self.bot.started_at, "R"))
        embed.add_field(name="Servidores", value=str(len(self.bot.guilds)))
        embed.add_field(name="Modalidades", value=" · ".join(GAME_MODES), inline=False)
        embed.add_field(name="Rangos", value=" · ".join(RANKS), inline=False)
        embed.add_field(
            name="Tecnología",
            value=f"Python {platform.python_version()} · discord.py {discord.__version__}",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: BoomBot) -> None:
    await bot.add_cog(Core(bot))
