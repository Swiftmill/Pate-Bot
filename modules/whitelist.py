from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from database.manager import DatabaseManager
from utils.embeds import create_embed
from utils.checks import whitelist_check


class AdminGroup(app_commands.Group):
    def __init__(self, cog: "WhitelistCog") -> None:
        super().__init__(name="admin", description="Commandes secrètes de la Pâte")
        self.cog = cog

    @app_commands.command(name="whitelist_add", description="Ajoute un membre à la whitelist sacrée.")
    @whitelist_check()
    async def whitelist_add(self, interaction: discord.Interaction, membre: discord.Member) -> None:
        await self.cog.db.execute("UPDATE users SET whitelist = 1 WHERE user_id = ?", (membre.id,))
        await interaction.response.send_message(embed=create_embed("Whitelist", f"{membre} rejoint le cercle intérieur."))

    @app_commands.command(name="whitelist_remove", description="Retire un membre du cercle.")
    @whitelist_check()
    async def whitelist_remove(self, interaction: discord.Interaction, membre: discord.Member) -> None:
        await self.cog.db.execute("UPDATE users SET whitelist = 0 WHERE user_id = ?", (membre.id,))
        await interaction.response.send_message(embed=create_embed("Whitelist", f"{membre} est renvoyé parmi les fidèles."))

    @app_commands.command(name="whitelist_list", description="Affiche la liste sanctifiée.")
    @whitelist_check()
    async def whitelist_list(self, interaction: discord.Interaction) -> None:
        rows = await self.cog.db.fetchall("SELECT user_id FROM users WHERE whitelist = 1", ())
        if not rows:
            await interaction.response.send_message("Personne n'est sanctifié pour l'instant.", ephemeral=True)
            return
        mentions = [f"<@{row['user_id']}>" for row in rows]
        await interaction.response.send_message(embed=create_embed("Whitelist", "\n".join(mentions)))


class WhitelistCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: DatabaseManager = bot.database  # type: ignore[attr-defined]
        self.group = AdminGroup(self)


async def setup(bot: commands.Bot) -> None:
    cog = WhitelistCog(bot)
    bot.tree.add_command(cog.group)
    await bot.add_cog(cog)
