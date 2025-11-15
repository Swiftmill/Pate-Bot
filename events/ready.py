from __future__ import annotations

import logging

from discord.ext import commands


class Ready(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logging.info("Synchronised commands: %s", getattr(self.bot, "synced", False))


def setup(bot: commands.Bot) -> None:
    raise RuntimeError("Use async setup")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ready(bot))
