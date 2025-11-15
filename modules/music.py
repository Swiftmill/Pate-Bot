from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict, List, Optional

import discord
from discord.ext import commands

from database.manager import DatabaseManager
from music.ytdl import MusicTrack
from utils.embeds import create_embed


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: DatabaseManager = bot.database  # type: ignore[attr-defined]
        self.queues: Dict[int, List[MusicTrack]] = defaultdict(list)
        self.current: Dict[int, Optional[MusicTrack]] = defaultdict(lambda: None)
        self.volumes: Dict[int, int] = defaultdict(lambda: 100)
        self.bot.loop.create_task(self._restore_queues())

    async def _restore_queues(self) -> None:
        await self.bot.wait_until_ready()
        rows = await self.db.fetchall(
            "SELECT guild_id, url, title, requested_by FROM music_queue ORDER BY position ASC",
            (),
        )
        for row in rows:
            track = MusicTrack(
                url=row["url"],
                title=row["title"],
                stream_url=row["url"],
                requested_by=row["requested_by"],
            )
            self.queues[row["guild_id"]].append(track)

    async def _store_queue(self, guild_id: int) -> None:
        await self.db.execute("DELETE FROM music_queue WHERE guild_id = ?", (guild_id,))
        queue = self.queues.get(guild_id, [])
        for position, track in enumerate(queue, start=1):
            await self.db.execute(
                "INSERT INTO music_queue (guild_id, url, title, requested_by, position) VALUES (?, ?, ?, ?, ?)",
                (guild_id, track.url, track.title, track.requested_by, position),
            )

    async def _ensure_voice(self, ctx: commands.Context) -> Optional[discord.VoiceClient]:
        guild = ctx.guild
        if not guild:
            return None
        voice = guild.voice_client
        channel = None
        if isinstance(ctx, commands.Context) and ctx.author.voice:
            channel = ctx.author.voice.channel
        if ctx.interaction and ctx.interaction.user.voice:
            channel = ctx.interaction.user.voice.channel
        if not channel:
            if ctx.interaction and not ctx.interaction.response.is_done():
                await ctx.interaction.response.send_message("Connecte-toi à un canal vocal sacré.", ephemeral=True)
            elif isinstance(ctx, commands.Context):
                await ctx.send("Connecte-toi à un canal vocal sacré.")
            return None
        if voice:
            if voice.channel != channel:
                await voice.move_to(channel)
        else:
            voice = await channel.connect()
        return voice

    async def _play_next(self, guild_id: int) -> None:
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
        voice = guild.voice_client
        queue = self.queues.get(guild_id)
        if not voice or not queue:
            self.current[guild_id] = None
            return
        track = queue.pop(0)
        if track.stream_url == track.url:
            # need to refresh stream info
            track = await MusicTrack.create(track.url, track.requested_by)
        self.current[guild_id] = track

        async def after_track(error: Optional[Exception]) -> None:
            if error:
                print(f"Erreur audio: {error}")
            await self._store_queue(guild_id)
            await self._play_next(guild_id)

        audio = track.to_audio()
        volume = self.volumes[guild_id] / 100
        source = discord.PCMVolumeTransformer(audio, volume=volume)
        voice.play(
            source,
            after=lambda err: asyncio.run_coroutine_threadsafe(after_track(err), self.bot.loop),
        )
        await self._store_queue(guild_id)

    @commands.hybrid_command(name="join", description="Invite Pâte Graphique dans ton canal.")
    async def join(self, ctx: commands.Context) -> None:
        voice = await self._ensure_voice(ctx)
        if not voice:
            return
        message = "Connexion établie au canal sacré."
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.interaction.response.send_message(message)
        else:
            await ctx.send(message)

    @commands.hybrid_command(name="play", description="Ajoute un chant depuis YouTube.")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        voice = await self._ensure_voice(ctx)
        if not voice:
            return
        track = await MusicTrack.create(query, ctx.author.id)
        self.queues[ctx.guild.id].append(track)
        await self._store_queue(ctx.guild.id)
        embed = create_embed("Titre ajouté", f"{track.title} a rejoint la file sacrée.")
        if not voice.is_playing() and not voice.is_paused() and not self.current.get(ctx.guild.id):
            await self._play_next(ctx.guild.id)
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.interaction.response.send_message(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="pause", description="Suspend le chant.")
    async def pause(self, ctx: commands.Context) -> None:
        voice = ctx.guild.voice_client if ctx.guild else None
        if voice and voice.is_playing():
            voice.pause()
            await ctx.reply("Lecture mise en pause.")
        else:
            await ctx.reply("Aucun chant en cours.")

    @commands.hybrid_command(name="resume", description="Relance le chant.")
    async def resume(self, ctx: commands.Context) -> None:
        voice = ctx.guild.voice_client if ctx.guild else None
        if voice and voice.is_paused():
            voice.resume()
            await ctx.reply("Le son mystique reprend.")
        else:
            await ctx.reply("Rien à reprendre.")

    @commands.hybrid_command(name="skip", description="Passe au suivant.")
    async def skip(self, ctx: commands.Context) -> None:
        voice = ctx.guild.voice_client if ctx.guild else None
        if voice and (voice.is_playing() or voice.is_paused()):
            voice.stop()
            await ctx.reply("Chant suivant invoqué.")
        else:
            await ctx.reply("La file est silencieuse.")

    @commands.hybrid_command(name="stop", description="Arrête tout et quitte.")
    async def stop(self, ctx: commands.Context) -> None:
        voice = ctx.guild.voice_client if ctx.guild else None
        if voice:
            voice.stop()
            await voice.disconnect()
        self.queues[ctx.guild.id].clear()
        self.current[ctx.guild.id] = None
        await self._store_queue(ctx.guild.id)
        await ctx.reply("Silence total. Le sanctuaire se vide.")

    @commands.hybrid_command(name="queue", description="Affiche la file actuelle.")
    async def queue(self, ctx: commands.Context) -> None:
        queue = self.queues.get(ctx.guild.id, [])
        if not queue:
            await ctx.reply("La file est vide.")
            return
        lines = [f"{index+1}. {track.title}" for index, track in enumerate(queue)]
        embed = create_embed("File sacrée", "\n".join(lines))
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="clear", description="Vide la file.")
    async def clear(self, ctx: commands.Context) -> None:
        self.queues[ctx.guild.id].clear()
        await self._store_queue(ctx.guild.id)
        await ctx.reply("File purifiée.")

    @commands.hybrid_command(name="nowplaying", description="Affiche le chant en cours.")
    async def nowplaying(self, ctx: commands.Context) -> None:
        current = self.current.get(ctx.guild.id)
        if not current:
            await ctx.reply("Le silence règne.")
            return
        member = ctx.guild.get_member(current.requested_by)
        requester = member.mention if member else f"<@{current.requested_by}>"
        embed = create_embed("Lecture actuelle", f"{current.title}\nDemandé par {requester}")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="volume", description="Ajuste le volume.")
    async def volume(self, ctx: commands.Context, niveau: int) -> None:
        niveau = max(1, min(200, niveau))
        self.volumes[ctx.guild.id] = niveau
        voice = ctx.guild.voice_client if ctx.guild else None
        if voice and voice.source and isinstance(voice.source, discord.PCMVolumeTransformer):
            voice.source.volume = niveau / 100
        await ctx.reply(f"Volume réglé sur {niveau}%.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
