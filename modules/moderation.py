from __future__ import annotations

import datetime as dt

import discord
from discord import app_commands
from discord.ext import commands

from database.manager import DatabaseManager
from utils.embeds import create_embed
from utils.checks import whitelist_check


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: DatabaseManager = bot.database  # type: ignore[attr-defined]

    @app_commands.command(name="ban", description="Bannis un membre en silence froid.")
    @app_commands.describe(membre="Cible", raison="Motif")
    @whitelist_check()
    async def ban(self, interaction: discord.Interaction, membre: discord.Member, raison: str | None = None) -> None:
        await interaction.guild.ban(membre, reason=raison)
        await interaction.response.send_message(embed=create_embed("Bannissement", f"{membre} est expulsé. Raison: {raison or 'non spécifiée'}"))

    @app_commands.command(name="kick", description="Expulse un membre.")
    @whitelist_check()
    async def kick(self, interaction: discord.Interaction, membre: discord.Member, raison: str | None = None) -> None:
        await interaction.guild.kick(membre, reason=raison)
        await interaction.response.send_message(embed=create_embed("Expulsion", f"{membre} est rejeté du sanctuaire."))

    @app_commands.command(name="mute", description="Réduit au silence un disciple.")
    @whitelist_check()
    async def mute(self, interaction: discord.Interaction, membre: discord.Member) -> None:
        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("Je n'ai pas la force de modérer.", ephemeral=True)
            return
        timeout_until = discord.utils.utcnow() + dt.timedelta(minutes=30)
        await membre.edit(timeout=timeout_until)
        await interaction.response.send_message(embed=create_embed("Silence", f"{membre} est réduit au silence pendant 30 minutes."))

    @app_commands.command(name="unmute", description="Rend la parole.")
    @whitelist_check()
    async def unmute(self, interaction: discord.Interaction, membre: discord.Member) -> None:
        await membre.edit(timeout=None)
        await interaction.response.send_message(embed=create_embed("Libération", f"{membre} peut parler à nouveau."))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
