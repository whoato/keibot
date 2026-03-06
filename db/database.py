from __future__ import annotations

import aiosqlite
from datetime import date, datetime, timedelta, timezone
from typing import Optional

_KST = timezone(timedelta(hours=9))


def _today_kst() -> date:
    return datetime.now(_KST).date()

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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id  INTEGER NOT NULL,
                role     TEXT NOT NULL,
                content  TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id        INTEGER PRIMARY KEY,
                chat_channel_id INTEGER
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
    today = _today_kst()

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


async def get_chat_channel(guild_id: int) -> Optional[int]:
    """길드의 채팅 채널 ID 반환. 미설정 시 None."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT chat_channel_id FROM guild_settings WHERE guild_id = ?", (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
        return row["chat_channel_id"] if row else None


async def set_chat_channel(guild_id: int, channel_id: int) -> None:
    """길드의 채팅 채널 ID 설정."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT INTO guild_settings (guild_id, chat_channel_id) VALUES (?, ?) "
            "ON CONFLICT(guild_id) DO UPDATE SET chat_channel_id = excluded.chat_channel_id",
            (guild_id, channel_id),
        )
        await db.commit()


async def check_points(guild_id: int, user_id: int, amount: int) -> bool:
    """포인트가 충분한지 확인. 차감하지 않음."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT points FROM users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()
        return row is not None and row["points"] >= amount


async def deduct_points(guild_id: int, user_id: int, amount: int) -> bool:
    """포인트 차감. 포인트가 부족하면 False 반환."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT points FROM users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()
        if row is None or row["points"] < amount:
            return False
        await db.execute(
            "UPDATE users SET points = points - ? WHERE guild_id = ? AND user_id = ?",
            (amount, guild_id, user_id),
        )
        await db.commit()
        return True


async def get_chat_history(guild_id: int, user_id: int, limit: int) -> list[dict]:
    """유저의 최근 대화 히스토리 반환 (오래된 순)."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT role, content FROM chat_history
               WHERE guild_id = ? AND user_id = ?
               ORDER BY id DESC LIMIT ?""",
            (guild_id, user_id, limit * 2),
        ) as cursor:
            rows = await cursor.fetchall()
        return [{"role": row["role"], "parts": [{"text": row["content"]}]} for row in reversed(rows)]


async def save_chat_pair(guild_id: int, user_id: int, user_msg: str, model_msg: str, limit: int) -> None:
    """user/model 메시지 쌍을 한 트랜잭션에 저장하고 limit 초과분 삭제."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.executemany(
            "INSERT INTO chat_history (guild_id, user_id, role, content) VALUES (?, ?, ?, ?)",
            [
                (guild_id, user_id, "user", user_msg),
                (guild_id, user_id, "model", model_msg),
            ],
        )
        await db.execute(
            """DELETE FROM chat_history WHERE id IN (
               SELECT id FROM chat_history
               WHERE guild_id = ? AND user_id = ?
               ORDER BY id ASC LIMIT MAX(0, (
                   SELECT COUNT(*) FROM chat_history WHERE guild_id = ? AND user_id = ?
               ) - ?)
            )""",
            (guild_id, user_id, guild_id, user_id, limit * 2),
        )
        await db.commit()


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
