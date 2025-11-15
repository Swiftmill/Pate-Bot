from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands

from config import phrases
from database.manager import DatabaseManager
from utils.embeds import create_embed
from utils.checks import ensure_profile


class Casino(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: DatabaseManager = bot.database  # type: ignore[attr-defined]

    async def _get_balance(self, user_id: int) -> int:
        await ensure_profile(self.db, user_id)
        row = await self.db.fetchone("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        return int(row["balance"]) if row else 0

    async def _add_balance(self, user_id: int, amount: int) -> None:
        await self.db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

    async def _record(self, user_id: int, action: str, context: str) -> None:
        await self.db.execute(
            "INSERT INTO activity_log (user_id, action, context) VALUES (?, ?, ?)",
            (user_id, action, context),
        )

    async def _wager(self, interaction: discord.Interaction, amount: int) -> bool:
        balance = await self._get_balance(interaction.user.id)
        if amount <= 0:
            await interaction.response.send_message("La mise doit être positive.", ephemeral=True)
            return False
        if balance < amount:
            await interaction.response.send_message("Tes GC tremblent: mise insuffisante.", ephemeral=True)
            return False
        await self._add_balance(interaction.user.id, -amount)
        return True

    @app_commands.command(name="roulette", description="Parie sur la roue sacrée.")
    async def roulette(self, interaction: discord.Interaction, choix: str, mise: int) -> None:
        choix = choix.lower()
        if not await self._wager(interaction, mise):
            return
        result_number = random.randint(0, 36)
        result_colour = "rouge" if result_number % 2 == 0 else "noir"
        win = False
        multiplier = 0
        if choix.isdigit():
            if int(choix) == result_number:
                win = True
                multiplier = 35
        elif choix in {"rouge", "noir"}:
            if choix == result_colour:
                win = True
                multiplier = 2
        payout = 0
        if win:
            payout = mise * multiplier
            await self._add_balance(interaction.user.id, payout)
        await self._record(interaction.user.id, "roulette", f"mise={mise};choix={choix};resultat={result_number}")
        desc = f"La roue s'arrête sur **{result_number} ({result_colour})**."
        if win:
            desc += f"\nTu empoches **{payout} GC**."
        else:
            desc += "\nLes ventilateurs se referment sur ta mise."
        embed = create_embed("Roue mystique", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Pile ou face sacré.")
    async def coinflip(self, interaction: discord.Interaction, choix: str, mise: int) -> None:
        choix = choix.lower()
        if choix not in {"pile", "face"}:
            await interaction.response.send_message("Choisis pile ou face.", ephemeral=True)
            return
        if not await self._wager(interaction, mise):
            return
        result = random.choice(["pile", "face"])
        win = result == choix
        if win:
            await self._add_balance(interaction.user.id, mise * 2)
        await self._record(interaction.user.id, "coinflip", f"mise={mise};choix={choix};resultat={result}")
        desc = f"La pièce tourbillonne et révèle **{result}**."
        desc += " Victoire." if win else " La chance t'échappe."
        embed = create_embed("Pièce du destin", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slots", description="Fais tourner les bobines lunaires.")
    async def slots(self, interaction: discord.Interaction, mise: int) -> None:
        if not await self._wager(interaction, mise):
            return
        symbols = ["🍜", "🎰", "🌀", "🔱", "💾", "🖥️"]
        result = [random.choice(symbols) for _ in range(3)]
        payout = 0
        if len(set(result)) == 1:
            payout = mise * 10
        elif len(set(result)) == 2:
            payout = mise * 3
        if payout:
            await self._add_balance(interaction.user.id, payout)
        await self._record(interaction.user.id, "slots", f"mise={mise};result={'/'.join(result)}")
        desc = " | ".join(result)
        desc += f"\nGain: **{payout} GC**" if payout else "\nLa machine soupire et avale ta mise."
        embed = create_embed("Bobines sacrées", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="blackjack", description="Affronte le croupier du flux.")
    async def blackjack(self, interaction: discord.Interaction, mise: int) -> None:
        if not await self._wager(interaction, mise):
            return
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(deck)

        def draw() -> int:
            return deck.pop()

        def hand_value(hand: list[int]) -> int:
            total = sum(hand)
            aces = hand.count(11)
            while total > 21 and aces:
                total -= 10
                aces -= 1
            return total

        player = [draw(), draw()]
        dealer = [draw(), draw()]

        while hand_value(player) < 17:
            player.append(draw())
        while hand_value(dealer) < 17:
            dealer.append(draw())

        player_val = hand_value(player)
        dealer_val = hand_value(dealer)
        desc = f"Toi: {player} = {player_val}\nCulte: {dealer} = {dealer_val}"
        if player_val > 21 or (dealer_val <= 21 and dealer_val >= player_val):
            desc += "\nLe croupier sacré récupère ta mise."
        else:
            gain = mise * 2
            await self._add_balance(interaction.user.id, gain)
            desc += f"\nTu triomphes et gagnes **{gain} GC**."
        await self._record(interaction.user.id, "blackjack", desc)
        embed = create_embed("Blackjack mystique", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="crash", description="Tiens la courbe du flux jusqu'à la rupture.")
    async def crash(self, interaction: discord.Interaction, mise: int) -> None:
        if not await self._wager(interaction, mise):
            return
        multiplier = 1.0
        history = []
        while True:
            increment = random.uniform(0.1, 0.8)
            multiplier += increment
            history.append(multiplier)
            if random.random() < 0.2 or multiplier > 10:
                break
        cashout = random.choice(history)
        crashed = history[-1]
        win = cashout != crashed
        desc = " → ".join(f"{value:.2f}x" for value in history)
        if win:
            gain = int(mise * cashout)
            await self._add_balance(interaction.user.id, gain)
            desc += f"\nTu t'éjectes à **{cashout:.2f}x** et récoltes **{gain} GC**."
        else:
            desc += "\nLe flux sature et dévore ta mise."
        await self._record(interaction.user.id, "crash", desc)
        embed = create_embed("Crash cosmique", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="duel", description="Affronte un disciple dans un duel de GC.")
    async def duel(self, interaction: discord.Interaction, membre: discord.Member, mise: int) -> None:
        if membre.bot:
            await interaction.response.send_message("Les automates ne sont pas dignes du duel.", ephemeral=True)
            return
        if membre.id == interaction.user.id:
            await interaction.response.send_message("Tu ne peux pas te défier toi-même.", ephemeral=True)
            return
        if not await self._wager(interaction, mise):
            return
        balance_other = await self._get_balance(membre.id)
        if balance_other < mise:
            await self._add_balance(interaction.user.id, mise)
            await interaction.response.send_message("Ton adversaire n'a pas assez de GC.", ephemeral=True)
            return
        await self._add_balance(membre.id, -mise)
        winner = random.choice([interaction.user, membre])
        total = mise * 2
        await self._add_balance(winner.id, total)
        desc = f"{interaction.user.mention} affronte {membre.mention}.\nLe vainqueur est {winner.mention}, récoltant **{total} GC**."
        embed = create_embed("Duel rituel", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="lottery", description="Participe à la loterie sacrée.")
    async def lottery(self, interaction: discord.Interaction) -> None:
        tickets = 1
        await ensure_profile(self.db, interaction.user.id)
        await self.db.execute(
            "INSERT INTO lottery_pool (guild_id, user_id, tickets) VALUES (?, ?, ?) ON CONFLICT(guild_id, user_id) DO UPDATE SET tickets = tickets + ?",
            (interaction.guild_id, interaction.user.id, tickets, tickets),
        )
        await interaction.response.send_message("Ton nom est gravé sur la roue céleste.")

    @app_commands.command(name="lottery_draw", description="Tire un gagnant de la loterie.")
    async def lottery_draw(self, interaction: discord.Interaction) -> None:
        rows = await self.db.fetchall("SELECT user_id, tickets FROM lottery_pool WHERE guild_id = ?", (interaction.guild_id,))
        if not rows:
            await interaction.response.send_message("Aucun ticket, aucun destin.", ephemeral=True)
            return
        population = []
        for row in rows:
            population.extend([row["user_id"]] * row["tickets"])
        winner_id = random.choice(population)
        prize = random.randint(1000, 3000)
        await self._add_balance(winner_id, prize)
        await self.db.execute("DELETE FROM lottery_pool WHERE guild_id = ?", (interaction.guild_id,))
        member = interaction.guild.get_member(winner_id) if interaction.guild else None
        winner_name = member.mention if member else f"<@{winner_id}>"
        desc = f"{winner_name} reçoit **{prize} GC**. Les autres méditent sur leur défaite."
        embed = create_embed("Loterie transcendante", desc)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slots_auto", description="Joue plusieurs machines à la suite.")
    async def slots_auto(self, interaction: discord.Interaction, mise: int, tours: int) -> None:
        if tours <= 0 or tours > 20:
            await interaction.response.send_message("Choisis entre 1 et 20 tours.", ephemeral=True)
            return
        balance = await self._get_balance(interaction.user.id)
        if balance < mise * tours:
            await interaction.response.send_message("Tu n'as pas assez de GC pour cette session.", ephemeral=True)
            return
        total_gain = 0
        symbols = ["🍜", "🎰", "🌀", "🔱", "💾", "🖥️"]
        for _ in range(tours):
            await self._add_balance(interaction.user.id, -mise)
            result = [random.choice(symbols) for _ in range(3)]
            payout = 0
            if len(set(result)) == 1:
                payout = mise * 10
            elif len(set(result)) == 2:
                payout = mise * 3
            if payout:
                await self._add_balance(interaction.user.id, payout)
                total_gain += payout - mise
            else:
                total_gain -= mise
        desc = f"Après {tours} tours, ton bilan est de {total_gain} GC."
        embed = create_embed("Marathon de bobines", desc)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Casino(bot))
