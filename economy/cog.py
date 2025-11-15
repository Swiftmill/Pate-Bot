from __future__ import annotations

import datetime as dt
import random
import sqlite3
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from config import phrases
from database.manager import DatabaseManager
from utils.embeds import create_embed
from utils.checks import ensure_profile


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: DatabaseManager = bot.database  # type: ignore[attr-defined]

    async def _get_user(self, user_id: int) -> sqlite3.Row:
        await ensure_profile(self.db, user_id)
        row = await self.db.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if row is None:
            raise RuntimeError("User row missing")
        return row

    async def _add_balance(self, user_id: int, amount: int) -> None:
        await self.db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )

    async def _add_xp(self, user_id: int, xp: int) -> Optional[int]:
        await self.db.execute(
            "UPDATE users SET experience = experience + ? WHERE user_id = ?",
            (xp, user_id),
        )
        row = await self._get_user(user_id)
        exp = row["experience"]
        level = row["level"]
        needed = level * 150
        if exp >= needed:
            new_level = level + 1
            await self.db.execute(
                "UPDATE users SET level = level + 1, experience = experience - ? WHERE user_id = ?",
                (needed, user_id),
            )
            return new_level
        return None

    async def _timestamp_action(self, user_id: int, column: str) -> None:
        now = dt.datetime.utcnow().isoformat()
        await self.db.execute(
            f"UPDATE users SET {column} = ? WHERE user_id = ?",
            (now, user_id),
        )

    async def _can_use(self, row: sqlite3.Row, column: str, delta: dt.timedelta) -> bool:
        value = row[column]
        if not value:
            return True
        last = dt.datetime.fromisoformat(value)
        return dt.datetime.utcnow() - last >= delta

    economy_group = app_commands.Group(name="job", description="Travaille pour le culte.")

    @economy_group.command(name="work", description="Accomplis ton office sacré pour gagner des GC.")
    async def work(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        row = await self._get_user(interaction.user.id)
        job = row["job"] or random.choice(phrases.JOBS)
        reward = random.randint(120, 320)
        await self._add_balance(interaction.user.id, reward)
        level_up = await self._add_xp(interaction.user.id, random.randint(40, 80))
        await self._timestamp_action(interaction.user.id, "last_bonus")
        flavour = phrases.personality_line("casino")
        desc = f"En tant que **{job}**, tu récoltes **{reward} GC**.\n{flavour}"
        if level_up:
            desc += f"\n\n✨ Tu montes au niveau **{level_up}** !"
        embed = create_embed("Travail accompli", desc)
        await interaction.followup.send(embed=embed)

    @economy_group.command(name="set", description="Change ta vocation sacrée.")
    @app_commands.choices(job=[app_commands.Choice(name=name, value=name) for name in phrases.JOBS])
    async def set_job(self, interaction: discord.Interaction, job: app_commands.Choice[str]) -> None:
        await self.db.execute("UPDATE users SET job = ? WHERE user_id = ?", (job.value, interaction.user.id))
        embed = create_embed("Vocation gravée", f"Tu deviens **{job.value}**. Ta loyauté est notée.")
        await interaction.response.send_message(embed=embed)

    @economy_group.command(name="list", description="Consulte les offices disponibles.")
    async def list_jobs(self, interaction: discord.Interaction) -> None:
        description = "\n".join(f"• {name}" for name in phrases.JOBS)
        embed = create_embed("Offices sacrés", description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="daily", description="Réclame ton tribut quotidien.")
    async def daily(self, interaction: discord.Interaction) -> None:
        row = await self._get_user(interaction.user.id)
        if not await self._can_use(row, "last_daily", dt.timedelta(hours=20)):
            await interaction.response.send_message("La marmite refroidit encore. Reviens plus tard.", ephemeral=True)
            return
        reward = 500
        await self._add_balance(interaction.user.id, reward)
        await self._timestamp_action(interaction.user.id, "last_daily")
        level_up = await self._add_xp(interaction.user.id, 120)
        desc = f"Tu récoltes **{reward} GC** en hommage quotidien."
        if level_up:
            desc += f"\n\n✨ Niveau augmenté: **{level_up}**."
        embed = create_embed("Dîme journalière", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="weekly", description="Réclame l'offrande hebdomadaire.")
    async def weekly(self, interaction: discord.Interaction) -> None:
        row = await self._get_user(interaction.user.id)
        if not await self._can_use(row, "last_weekly", dt.timedelta(days=6)):
            await interaction.response.send_message("La salle du conseil reste fermée. Reviens plus tard.", ephemeral=True)
            return
        reward = 2000
        await self._add_balance(interaction.user.id, reward)
        await self._timestamp_action(interaction.user.id, "last_weekly")
        await self._add_xp(interaction.user.id, 320)
        embed = create_embed("Offrande hebdomadaire", f"Le sanctuaire te remet **{reward} GC**.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bonus", description="Réclame une impulsion mystique.")
    async def bonus(self, interaction: discord.Interaction) -> None:
        row = await self._get_user(interaction.user.id)
        if not await self._can_use(row, "last_bonus", dt.timedelta(hours=6)):
            await interaction.response.send_message("Les bobines ne sont pas prêtes. Reviens plus tard.", ephemeral=True)
            return
        reward = random.randint(80, 160)
        await self._add_balance(interaction.user.id, reward)
        await self._timestamp_action(interaction.user.id, "last_bonus")
        embed = create_embed("Flux supplémentaire", f"La couronne thermique t'offre **{reward} GC**.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventory", description="Consulte tes reliques.")
    async def inventory(self, interaction: discord.Interaction) -> None:
        rows = await self.db.fetchall(
            "SELECT item, quantity FROM inventory WHERE user_id = ?",
            (interaction.user.id,),
        )
        if not rows:
            await interaction.response.send_message("Ton inventaire est vide mais ton âme est pleine.", ephemeral=True)
            return
        description = "\n".join(f"• {row['item']}: {row['quantity']}" for row in rows)
        embed = create_embed("Inventaire sacré", description)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="shop", description="Parcoures le bazar sacré.")
    async def shop(self, interaction: discord.Interaction) -> None:
        lines = [f"**{item['name']}** — {item['price']} GC ({item['rarity']})" for item in phrases.SHOP_ITEMS]
        embed = create_embed("Boutique mystique", "\n".join(lines))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Achète un objet du bazar.")
    @app_commands.describe(item="Nom de l'objet à acquérir")
    async def buy(self, interaction: discord.Interaction, item: str) -> None:
        choice = next((entry for entry in phrases.SHOP_ITEMS if entry["name"].lower() == item.lower()), None)
        if not choice:
            await interaction.response.send_message("Aucun objet de ce nom dans la vitrine sacrée.", ephemeral=True)
            return
        row = await self._get_user(interaction.user.id)
        if row["balance"] < choice["price"]:
            await interaction.response.send_message("Tes GC sont trop maigres pour cette relique.", ephemeral=True)
            return
        await self._add_balance(interaction.user.id, -choice["price"])
        await self.db.execute(
            "INSERT INTO inventory (user_id, item, quantity) VALUES (?, ?, 1) ON CONFLICT(user_id, item) DO UPDATE SET quantity = quantity + 1",
            (interaction.user.id, choice["name"]),
        )
        await self._add_xp(interaction.user.id, 60)
        embed = create_embed("Acquisition", f"Tu obtiens **{choice['name']}** pour **{choice['price']} GC**.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sell", description="Revends un objet.")
    async def sell(self, interaction: discord.Interaction, item: str) -> None:
        choice = next((entry for entry in phrases.SHOP_ITEMS if entry["name"].lower() == item.lower()), None)
        if not choice:
            await interaction.response.send_message("Cet objet n'est pas reconnu.", ephemeral=True)
            return
        row = await self.db.fetchone(
            "SELECT quantity FROM inventory WHERE user_id = ? AND item = ?",
            (interaction.user.id, choice["name"]),
        )
        if not row or row["quantity"] <= 0:
            await interaction.response.send_message("Tu ne possèdes pas cette relique.", ephemeral=True)
            return
        await self.db.execute(
            "UPDATE inventory SET quantity = quantity - 1 WHERE user_id = ? AND item = ?",
            (interaction.user.id, choice["name"]),
        )
        await self._add_balance(interaction.user.id, choice["price"] // 2)
        embed = create_embed("Transaction", f"Tu revends **{choice['name']}** et reçois **{choice['price'] // 2} GC**.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="profile", description="Consulte ton profil sacré.")
    async def profile(self, interaction: discord.Interaction, member: Optional[discord.Member] = None) -> None:
        target = member or interaction.user
        row = await self._get_user(target.id)
        embed = create_embed(
            "Profil sacré",
            f"**Job**: {row['job']}\n**GC**: {row['balance']}\n**XP**: {row['experience']}\n**Niveau**: {row['level']}",
            footer=phrases.personality_line("casino"),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="level", description="Consulte ton niveau mystique.")
    async def level(self, interaction: discord.Interaction) -> None:
        row = await self._get_user(interaction.user.id)
        needed = row["level"] * 150
        embed = create_embed(
            "Progression",
            f"Niveau **{row['level']}** — XP: {row['experience']}/{needed}",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    cog = Economy(bot)
    bot.tree.add_command(cog.economy_group)
    await bot.add_cog(cog)
