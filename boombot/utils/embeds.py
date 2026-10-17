"""Helpers para construir embeds con la identidad visual de BoomNetwork."""

from __future__ import annotations

import discord

from ..constants import BRAND_COLOR, NETWORK_NAME


def brand_embed(title: str, description: str | None = None) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, colour=discord.Colour(BRAND_COLOR))
    embed.set_footer(text=NETWORK_NAME)
    return embed
