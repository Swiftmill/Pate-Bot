import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands

from config.settings import Settings
from database.manager import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)


class PateBot(commands.Bot):
    """Discord bot for the Pâte Graphique cult."""

    def __init__(self, settings: Settings, database: DatabaseManager) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix=settings.prefix,
            intents=intents,
            application_id=settings.application_id,
        )
        self.settings = settings
        self.database = database
        self.synced = False

    async def setup_hook(self) -> None:
        await self.database.initialise()
        base_path = Path(__file__).parent

        for extension in self.settings.extensions:
            try:
                await self.load_extension(extension)
                logging.info("Loaded extension %s", extension)
            except Exception as exc:  # pragma: no cover - startup log
                logging.exception("Failed to load extension %s: %s", extension, exc)

        if self.settings.sync_commands:
            await self.tree.sync()
            self.synced = True

    async def on_ready(self) -> None:
        logging.info("Bot ready as %s", self.user)
        activity = discord.Game(name="Louange aux Pâtes Graphiques")
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def close(self) -> None:
        await super().close()
        await self.database.close()


async def main() -> None:
    settings = Settings.from_env()
    database = DatabaseManager(settings.database_path)
    bot = PateBot(settings, database)

    async with bot:
        await bot.start(settings.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown requested by user")
