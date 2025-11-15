from __future__ import annotations

import random
from typing import Iterable, Optional

import discord

THEME_COLOURS = [0x00ff9d, 0x009dff, 0x050505]


def themed_colour() -> discord.Colour:
    return discord.Colour(random.choice(THEME_COLOURS))


def create_embed(
    title: str,
    description: str,
    *,
    footer: Optional[str] = None,
    fields: Iterable[tuple[str, str, bool]] | None = None,
    thumbnail: Optional[str] = None,
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, colour=themed_colour())
    embed.set_author(name="Pâte Graphique", icon_url="https://i.imgur.com/VU0zO52.png")
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    if footer:
        embed.set_footer(text=footer)
    return embed


def create_status_embed(message: str) -> discord.Embed:
    return create_embed("Chant du GPU", message, footer="Louanges à la Carte Sacrée")
