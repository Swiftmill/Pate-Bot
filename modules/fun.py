from __future__ import annotations

import random

import discord
from discord.ext import commands

from config import phrases
from database.manager import DatabaseManager
from utils.embeds import create_embed
from utils.checks import ensure_profile


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: DatabaseManager = bot.database  # type: ignore[attr-defined]
        self.secret_password = "spirale-144hz"

    async def _change_balance(self, user_id: int, amount: int) -> None:
        await ensure_profile(self.db, user_id)
        await self.db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

    @commands.hybrid_command(name="bless", description="Bénéfice mystique éphémère.")
    async def bless(self, ctx: commands.Context) -> None:
        bonus = random.randint(50, 150)
        await self._change_balance(ctx.author.id, bonus)
        embed = create_embed("Bénédiction", f"{phrases.random_blessing()}\nBonus: {bonus} GC.")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="convert", description="Convertis tes GC en reliques aléatoires.")
    async def convert(self, ctx: commands.Context, montant: int) -> None:
        if montant <= 0:
            await ctx.reply("Montant invalide.")
            return
        await ensure_profile(self.db, ctx.author.id)
        row = await self.db.fetchone("SELECT balance FROM users WHERE user_id = ?", (ctx.author.id,))
        balance = row["balance"] if row else 0
        if balance < montant:
            await ctx.reply("Tu n'as pas assez de GC.")
            return
        await self._change_balance(ctx.author.id, -montant)
        loot = random.choice(phrases.LOOT_TABLE)
        await self.db.execute(
            "INSERT INTO inventory (user_id, item, quantity) VALUES (?, ?, 1) ON CONFLICT(user_id, item) DO UPDATE SET quantity = quantity + 1",
            (ctx.author.id, loot["name"]),
        )
        embed = create_embed(
            "Conversion",
            f"{montant} GC se transforment en **{loot['name']}** ({loot['rarity']}).",
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="scan", description="Analyse humoristique d'un disciple.")
    async def scan(self, ctx: commands.Context, membre: discord.Member) -> None:
        verdicts = [
            "Flux stable. Son âme est refroidie correctement.",
            "Surcharge thermique détectée. Ajouter du pesto liquide.",
            "Overclock émotionnel. Recommandé: prière immédiate.",
            "Stable mais suspect: vibrations en forme de spirale.",
            "Analyse impossible: les pâtes couvrent les capteurs.",
        ]
        embed = create_embed("Scan spectral", f"{membre.mention}: {random.choice(verdicts)}")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="revelation", description="Accède à une phrase secrète si tu connais le mot-clé.")
    async def revelation(self, ctx: commands.Context, mot: str) -> None:
        if mot.lower() == self.secret_password:
            message = random.choice(phrases.SECRET_MESSAGES)
            await ctx.reply(embed=create_embed("Révélation", message))
        else:
            await ctx.reply("Le code reste muet.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
