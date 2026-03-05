import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]
DB_PATH: str = os.getenv("DB_PATH", "kei.db")
DEV_GUILD_ID: int | None = int(os.environ["DEV_GUILD_ID"]) if os.getenv("DEV_GUILD_ID") else None

# 포인트 설정
BASE_POINTS: int = 10
STREAK_BONUS_POINTS: int = 50
STREAK_BONUS_INTERVAL: int = 7  # 7일마다 보너스
