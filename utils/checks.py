from __future__ import annotations

from typing import Callable

import discord
from discord import app_commands

from database.manager import DatabaseManager


def whitelist_check() -> Callable[[app_commands.Command], app_commands.Command]:  # type: ignore[name-defined]
    async def predicate(interaction: discord.Interaction) -> bool:
        db: DatabaseManager = interaction.client.database  # type: ignore[attr-defined]
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (interaction.user.id,))
        row = await db.fetchone(
            "SELECT whitelist FROM users WHERE user_id = ?",
            (interaction.user.id,),
        )
        if not row or not row["whitelist"]:
            raise app_commands.CheckFailure("Tu n'es pas sanctifié par le conseil des Pâtes.")
        return True

    return app_commands.check(predicate)


async def ensure_profile(database: DatabaseManager, user_id: int) -> None:
    await database.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
