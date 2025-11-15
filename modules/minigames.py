from __future__ import annotations

import random
from typing import Dict, Optional

import discord
from discord import app_commands
from discord.ext import commands

from config import phrases
from database.manager import DatabaseManager
from utils.embeds import create_embed
from utils.checks import ensure_profile


class QuizView(discord.ui.View):
    def __init__(self, question: dict, author_id: int, reward_callback) -> None:
        super().__init__(timeout=30)
        self.question = question
        self.author_id = author_id
        self.reward_callback = reward_callback
        for index, option in enumerate(question["options"]):
            self.add_item(QuizButton(index, option, question["answer"], reward_callback))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id


class QuizButton(discord.ui.Button):
    def __init__(self, index: int, label: str, answer: int, reward_callback) -> None:
        super().__init__(style=discord.ButtonStyle.secondary, label=label)
        self.index = index
        self.answer = answer
        self.reward_callback = reward_callback

    async def callback(self, interaction: discord.Interaction) -> None:
        correct = self.index == self.answer
        if correct:
            await self.reward_callback(interaction.user.id, success=True)
            await interaction.response.send_message("Exact. Les circuits applaudissent.", ephemeral=True)
        else:
            await self.reward_callback(interaction.user.id, success=False)
            await interaction.response.send_message("Faux. Le GPU soupire.", ephemeral=True)
        self.view.stop()


class MiniGames(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: DatabaseManager = bot.database  # type: ignore[attr-defined]
        self.active_quests: Dict[int, str] = {}

    async def _reward(self, user_id: int, coins: int, xp: int) -> None:
        await ensure_profile(self.db, user_id)
        await self.db.execute(
            "UPDATE users SET balance = balance + ?, experience = experience + ? WHERE user_id = ?",
            (coins, xp, user_id),
        )

    @commands.hybrid_command(name="adventure", description="Pars dans une aventure longue.")
    async def adventure(self, ctx: commands.Context) -> None:
        scenario = random.choice(phrases.LONG_GAMES)
        reward = random.randint(200, 450)
        xp = random.randint(120, 220)
        await self._reward(ctx.author.id, reward, xp)
        embed = create_embed(
            "Procession aventureuse",
            f"{scenario}\n\nRécompense: **{reward} GC**, **{xp} XP**",
            footer=phrases.personality_line("minigame"),
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="quest", description="Système de quêtes mystiques.")
    @app_commands.describe(action="list/start/finish", nom="Nom de la quête")
    async def quest(self, ctx: commands.Context, action: str, nom: Optional[str] = None) -> None:
        action = action.lower()
        if action == "list":
            lines = [f"• {name}" for name in phrases.LONG_GAMES[:20]]
            embed = create_embed("Quêtes disponibles", "\n".join(lines))
            await ctx.reply(embed=embed)
            return
        if action == "start":
            if not nom:
                await ctx.reply("Précise la quête.")
                return
            if nom not in phrases.LONG_GAMES:
                await ctx.reply("Cette quête n'a pas été bénie.")
                return
            self.active_quests[ctx.author.id] = nom
            await ctx.reply(f"Quête **{nom}** engagée. Reviens pour la conclure.")
            return
        if action == "finish":
            quest_name = self.active_quests.pop(ctx.author.id, None)
            if not quest_name:
                await ctx.reply("Aucune quête en cours.")
                return
            reward = random.randint(400, 800)
            xp = random.randint(200, 400)
            await self._reward(ctx.author.id, reward, xp)
            embed = create_embed(
                "Quête conclue",
                f"{quest_name} s'achève. Tu reçois **{reward} GC** et **{xp} XP**.",
            )
            await ctx.reply(embed=embed)
            return
        await ctx.reply("Action inconnue.")

    @commands.hybrid_command(name="fight", description="Duel mystique contre un autre disciple.")
    async def fight(self, ctx: commands.Context, membre: discord.Member) -> None:
        if membre.bot:
            await ctx.reply("Les automates refusent le duel.")
            return
        outcome = random.choice([ctx.author, membre])
        loot = random.choice(phrases.LOOT_TABLE)
        reward = random.randint(150, 350)
        xp = random.randint(90, 150)
        await self._reward(outcome.id, reward, xp)
        desc = (
            f"{ctx.author.mention} affronte {membre.mention}.\n"
            f"**{outcome.mention}** remporte le duel, gagne {reward} GC, {xp} XP et trouve {loot['name']} ({loot['rarity']})."
        )
        embed = create_embed("Duel mystique", desc)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="open", description="Ouvre une lootbox sacrée.")
    async def open_lootbox(self, ctx: commands.Context) -> None:
        loot = random.choice(phrases.LOOT_TABLE)
        coins = random.randint(80, 220)
        await self._reward(ctx.author.id, coins, 60)
        embed = create_embed(
            "Reliquaire ouvert",
            f"Tu obtiens **{loot['name']}** ({loot['rarity']}) et {coins} GC.",
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="coop", description="Déclenche un événement coopératif.")
    async def coop(self, ctx: commands.Context) -> None:
        event = random.choice(phrases.COOP_EVENTS)
        participants = len(ctx.guild.members)
        reward = random.randint(100, 200)
        xp = random.randint(70, 120)
        await self._reward(ctx.author.id, reward, xp)
        embed = create_embed(
            "Rituel coopératif",
            f"{event}\nParticipants ressentis: {participants}. Récompense personnelle: {reward} GC / {xp} XP.",
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="quiz", description="Réponds à une énigme sacrée.")
    async def quiz(self, ctx: commands.Context) -> None:
        question = random.choice(phrases.QUIZZES)

        async def reward_callback(user_id: int, success: bool) -> None:
            if success:
                await self._reward(user_id, 120, 120)
            else:
                await self._reward(user_id, 20, 20)

        view = QuizView(question, ctx.author.id, reward_callback)
        embed = create_embed("Épreuve", question["question"])
        await ctx.reply(embed=embed, view=view)

    @commands.hybrid_command(name="minigame", description="Joue à un mini-jeu express.")
    async def minigame(self, ctx: commands.Context) -> None:
        activity = random.choice(phrases.SHORT_GAMES)
        reward = random.randint(60, 180)
        xp = random.randint(40, 100)
        await self._reward(ctx.author.id, reward, xp)
        embed = create_embed(
            "Mini-rituel",
            f"{activity}\nRécompense: {reward} GC / {xp} XP.",
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="boss", description="Affronte un boss du culte.")
    async def boss(self, ctx: commands.Context) -> None:
        boss = random.choice(phrases.BOSS_NAMES)
        ultimate = random.random() < 0.1
        hp = random.randint(500, 1200) if not ultimate else random.randint(1500, 2500)
        reward = random.randint(600, 1200) if not ultimate else random.randint(2000, 4000)
        xp = random.randint(250, 500) if not ultimate else random.randint(600, 900)
        await self._reward(ctx.author.id, reward, xp)
        text = f"Boss: **{boss}** — HP simulé: {hp}. Récompense: {reward} GC / {xp} XP."
        if ultimate:
            text += "\n⚠️ Mode Divin: tu entends les ventilateurs chanter une langue ancienne."
        embed = create_embed("Boss combattu", text)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="sacrifice", description="Offre un sacrifice mystique.")
    async def sacrifice(self, ctx: commands.Context) -> None:
        chance = random.random()
        if chance > 0.7:
            reward = 800
            xp = 300
            await self._reward(ctx.author.id, reward, xp)
            message = f"Le sacrifice réussit. Tu gagnes {reward} GC / {xp} XP."
        else:
            loss = 200
            await self._reward(ctx.author.id, -loss, 50)
            message = f"Le culte réclame {loss} GC. Tes XP se stabilisent."
        embed = create_embed("Sacrifice", message)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MiniGames(bot))
