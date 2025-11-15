from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


def _get_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    token: str
    application_id: int
    prefix: str = "!pg"
    database_path: str = "data/pate_graphique.sqlite3"
    sync_commands: bool = True
    extensions: List[str] = field(
        default_factory=lambda: [
            "events.ready",
            "modules.propaganda",
            "modules.music",
            "economy.cog",
            "casino.cog",
            "modules.minigames",
            "modules.moderation",
            "modules.whitelist",
            "modules.fun",
        ]
    )

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise RuntimeError("DISCORD_TOKEN must be set in environment")
        application_id_str = os.getenv("DISCORD_APPLICATION_ID")
        if not application_id_str:
            raise RuntimeError("DISCORD_APPLICATION_ID must be set in environment")
        application_id = int(application_id_str)
        prefix = os.getenv("PATE_PREFIX", "!pg")
        database_path = os.getenv("PATE_DATABASE", "data/pate_graphique.sqlite3")
        sync_commands = _get_bool("PATE_SYNC", "true")

        return cls(
            token=token,
            application_id=application_id,
            prefix=prefix,
            database_path=database_path,
            sync_commands=sync_commands,
        )
