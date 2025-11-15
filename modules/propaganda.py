from __future__ import annotations

import random
import re

import discord
from discord.ext import commands

from config import phrases
from utils.embeds import create_embed

TRIGGERS = [
    r"p[aâ]te[s]?",
    r"graphique",
    r"gpu",
    r"carte graphique",
    r"pasta gpu cult",
]

TRIGGER_REGEX = re.compile("|".join(TRIGGERS), re.IGNORECASE)


class Propaganda(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.divine_mode = False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild:
            return

        content = message.content
        if TRIGGER_REGEX.search(content):
            reply = phrases.random_propaganda()
            await message.channel.send(reply)

        lowered = content.lower()
        for rare, response in phrases.BANNED_WORD_TRIGGERS.items():
            if rare in lowered:
                await message.channel.send(response)

        if self.divine_mode and random.randint(1, 50) == 42:
            await message.channel.send(phrases.DIVINE_MODE_MESSAGE)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if random.randint(1, 400) == 77:
            self.divine_mode = True
            if interaction.channel:
                await interaction.channel.send(phrases.DIVINE_MODE_MESSAGE)

    @commands.hybrid_command(name="pate", description="Reçoit une parole sacrée.")
    async def pate_command(self, ctx: commands.Context) -> None:
        line = phrases.random_propaganda()
        embed = create_embed("Oracle de la Pâte", line)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="pray", description="Reçois une bénédiction mystique.")
    async def pray(self, ctx: commands.Context) -> None:
        line = phrases.random_blessing()
        embed = create_embed("Bénédiction", line)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="gpuinfo", description="Apprends un fait sacré sur les GPU.")
    async def gpuinfo(self, ctx: commands.Context) -> None:
        fact = phrases.random_gpu_fact()
        embed = create_embed("Chronique du GPU", fact)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Propaganda(bot))
