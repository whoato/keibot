from __future__ import annotations

import aiosqlite
from datetime import date, timedelta
from typing import Optional

import config
from models.attendance import UserRecord, AttendanceResult


async def init_db() -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                guild_id    INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                username    TEXT NOT NULL,
                points      INTEGER DEFAULT 0,
                total_days  INTEGER DEFAULT 0,
                streak      INTEGER DEFAULT 0,
                last_attend DATE,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS attendance_log (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id      INTEGER NOT NULL,
                user_id       INTEGER NOT NULL,
                date          DATE NOT NULL,
                points_earned INTEGER DEFAULT 0,
                UNIQUE(guild_id, user_id, date),
                FOREIGN KEY (guild_id, user_id) REFERENCES users(guild_id, user_id)
            )
        """)
        await db.commit()


async def get_user(guild_id: int, user_id: int) -> Optional[UserRecord]:
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return UserRecord(
                guild_id=row["guild_id"],
                user_id=row["user_id"],
                username=row["username"],
                points=row["points"],
                total_days=row["total_days"],
                streak=row["streak"],
                last_attend=date.fromisoformat(row["last_attend"]) if row["last_attend"] else None,
            )


async def attend(guild_id: int, user_id: int, username: str) -> AttendanceResult:
    today = date.today()

    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # 유저 조회 또는 생성
        async with db.execute(
            "SELECT * FROM users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            # 신규 유저
            streak = 1
            points_earned = config.BASE_POINTS
            await db.execute(
                "INSERT INTO users (guild_id, user_id, username, points, total_days, streak, last_attend) VALUES (?, ?, ?, ?, 1, 1, ?)",
                (guild_id, user_id, username, points_earned, today.isoformat()),
            )
        else:
            last_attend = date.fromisoformat(row["last_attend"]) if row["last_attend"] else None

            if last_attend == today:
                return AttendanceResult(already_attended=True)

            if last_attend == today - timedelta(days=1):
                streak = row["streak"] + 1
            else:
                streak = 1

            points_earned = config.BASE_POINTS
            if streak % config.STREAK_BONUS_INTERVAL == 0:
                points_earned += config.STREAK_BONUS_POINTS

            await db.execute(
                """UPDATE users
                   SET username = ?, points = points + ?, total_days = total_days + 1,
                       streak = ?, last_attend = ?
                   WHERE guild_id = ? AND user_id = ?""",
                (username, points_earned, streak, today.isoformat(), guild_id, user_id),
            )

        # 출석 로그 기록
        await db.execute(
            "INSERT OR IGNORE INTO attendance_log (guild_id, user_id, date, points_earned) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, today.isoformat(), points_earned),
        )
        await db.commit()

    user = await get_user(guild_id, user_id)
    return AttendanceResult(
        already_attended=False,
        user=user,
        points_earned=points_earned,
        streak=streak,
        is_streak_bonus=streak % config.STREAK_BONUS_INTERVAL == 0,
    )


async def get_ranking(guild_id: int, limit: int = 10) -> list[UserRecord]:
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE guild_id = ? ORDER BY total_days DESC, points DESC LIMIT ?",
            (guild_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                UserRecord(
                    guild_id=row["guild_id"],
                    user_id=row["user_id"],
                    username=row["username"],
                    points=row["points"],
                    total_days=row["total_days"],
                    streak=row["streak"],
                    last_attend=date.fromisoformat(row["last_attend"]) if row["last_attend"] else None,
                )
                for row in rows
            ]


async def reset_user(guild_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
        ) as cursor:
            if await cursor.fetchone() is None:
                return False

        await db.execute(
            "UPDATE users SET points = 0, total_days = 0, streak = 0, last_attend = NULL WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        await db.execute(
            "DELETE FROM attendance_log WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
        )
        await db.commit()
        return True
