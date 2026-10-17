"""Prueba de humo: carga el módulo core SIN conectarse a Discord."""

import asyncio

import discord

from boombot.bot import BoomBot
from boombot.config import Settings


def test_core_extension_registers_commands():
    async def scenario() -> set[str]:
        bot = BoomBot(Settings(token="x" * 60))
        try:
            await bot.load_extension("boombot.cogs.core")
            return {cmd.name for cmd in bot.tree.get_commands()}
        finally:
            await bot.close()

    assert asyncio.run(scenario()) == {"ping", "info"}


def test_only_guilds_intent_enabled():
    async def scenario() -> discord.Intents:
        bot = BoomBot(Settings(token="x" * 60))
        try:
            return bot.intents
        finally:
            await bot.close()

    intents = asyncio.run(scenario())
    assert intents.guilds
    assert not intents.members
    assert not intents.message_content
    assert not intents.presences
