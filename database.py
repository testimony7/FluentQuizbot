import os
from datetime import datetime, timedelta, timezone

import aiosqlite

from bot.config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id          INTEGER PRIMARY KEY,
    username         TEXT,
    first_name       TEXT,
    level            TEXT    NOT NULL DEFAULT 'beginner',
    total_answered   INTEGER NOT NULL DEFAULT 0,
    total_correct    INTEGER NOT NULL DEFAULT 0,
    streak           INTEGER NOT NULL DEFAULT 0,
    best_streak      INTEGER NOT NULL DEFAULT 0,
    last_active      TEXT,
    daily_subscribed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS polls (
    poll_id        TEXT PRIMARY KEY,
    user_id        INTEGER NOT NULL,
    correct_option INTEGER NOT NULL,
    category       TEXT
);
"""


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


async def init_db() -> None:
    folder = os.path.dirname(DATABASE_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def upsert_user(user_id: int, username: str | None, first_name: str | None) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username, first_name),
        )
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def set_level(user_id: int, level: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET level = ? WHERE user_id = ?", (level, user_id))
        await db.commit()


async def save_poll(poll_id: str, user_id: int, correct_option: int, category: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO polls (poll_id, user_id, correct_option, category) VALUES (?, ?, ?, ?)",
            (poll_id, user_id, correct_option, category),
        )
        await db.commit()


async def pop_poll(poll_id: str) -> dict | None:
    """Fetch a poll and delete it so each poll is only scored once."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM polls WHERE poll_id = ?", (poll_id,))
        row = await cur.fetchone()
        if row:
            await db.execute("DELETE FROM polls WHERE poll_id = ?", (poll_id,))
            await db.commit()
        return dict(row) if row else None


async def record_answer(user_id: int, correct: bool) -> dict | None:
    """Update score and daily streak. Returns the updated user row."""
    user = await get_user(user_id)
    if user is None:
        return None

    today = _today()
    yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()

    streak = user["streak"]
    if user["last_active"] != today:
        streak = streak + 1 if user["last_active"] == yesterday else 1
    best = max(user["best_streak"], streak)

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE users SET
                total_answered = total_answered + 1,
                total_correct = total_correct + ?,
                streak = ?,
                best_streak = ?,
                last_active = ?
            WHERE user_id = ?
            """,
            (1 if correct else 0, streak, best, today, user_id),
        )
        await db.commit()
    return await get_user(user_id)


async def get_leaderboard(limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT first_name, username, total_correct, total_answered, best_streak
            FROM users WHERE total_answered > 0
            ORDER BY total_correct DESC, best_streak DESC LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in await cur.fetchall()]


async def toggle_daily(user_id: int) -> bool:
    """Flip daily-word subscription. Returns the new state."""
    user = await get_user(user_id)
    new_state = 0 if (user and user["daily_subscribed"]) else 1
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET daily_subscribed = ? WHERE user_id = ?", (new_state, user_id)
        )
        await db.commit()
    return bool(new_state)


async def get_daily_subscribers() -> list[int]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE daily_subscribed = 1")
        return [r[0] for r in await cur.fetchall()]
