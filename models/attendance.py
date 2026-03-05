from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class UserRecord:
    guild_id: int
    user_id: int
    username: str
    points: int
    total_days: int
    streak: int
    last_attend: Optional[date] = None


@dataclass
class AttendanceResult:
    already_attended: bool = False
    user: Optional[UserRecord] = None
    points_earned: int = 0
    streak: int = 0
    is_streak_bonus: bool = False
