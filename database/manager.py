from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    experience INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    last_daily TEXT,
    last_weekly TEXT,
    last_bonus TEXT,
    job TEXT DEFAULT 'Initié du Flux',
    whitelist INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER NOT NULL,
    item TEXT NOT NULL,
    quantity INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item)
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS music_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    requested_by INTEGER NOT NULL,
    position INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS lottery_pool (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    tickets INTEGER DEFAULT 1,
    PRIMARY KEY (guild_id, user_id)
);
"""


class DatabaseManager:
    """Simple async wrapper for sqlite3."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._conn: Optional[sqlite3.Connection] = None
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def initialise(self) -> None:
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        await self.execute_script(SCHEMA)

    async def close(self) -> None:
        if self._conn:
            await asyncio.to_thread(self._conn.close)
            self._conn = None

    async def execute(self, query: str, params: Iterable[Any] | None = None) -> None:
        if not self._conn:
            raise RuntimeError("Database connection not initialised")
        await asyncio.to_thread(self._conn.execute, query, params or [])
        await asyncio.to_thread(self._conn.commit)

    async def execute_script(self, script: str) -> None:
        if not self._conn:
            raise RuntimeError("Database connection not initialised")
        await asyncio.to_thread(self._conn.executescript, script)
        await asyncio.to_thread(self._conn.commit)

    async def fetchone(self, query: str, params: Iterable[Any] | None = None) -> Optional[sqlite3.Row]:
        if not self._conn:
            raise RuntimeError("Database connection not initialised")
        cursor = await asyncio.to_thread(self._conn.execute, query, params or [])
        row = cursor.fetchone()
        await asyncio.to_thread(cursor.close)
        return row

    async def fetchall(self, query: str, params: Iterable[Any] | None = None) -> list[sqlite3.Row]:
        if not self._conn:
            raise RuntimeError("Database connection not initialised")
        cursor = await asyncio.to_thread(self._conn.execute, query, params or [])
        rows = cursor.fetchall()
        await asyncio.to_thread(cursor.close)
        return rows
