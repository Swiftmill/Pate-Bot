from __future__ import annotations

import asyncio
from dataclasses import dataclass

import discord
import yt_dlp

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}

FFMPEG_OPTIONS = {
    "options": "-vn"
}


ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


@dataclass(slots=True)
class MusicTrack:
    url: str
    title: str
    stream_url: str
    requested_by: int

    @classmethod
    async def create(cls, query: str, requested_by: int) -> "MusicTrack":
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        if "entries" in data:
            data = data["entries"][0]
        return cls(
            url=data.get("webpage_url", query),
            title=data.get("title", "Flux inconnu"),
            stream_url=data["url"],
            requested_by=requested_by,
        )

    def to_audio(self) -> discord.AudioSource:
        return discord.FFmpegPCMAudio(self.stream_url, **FFMPEG_OPTIONS)
