import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]
DB_PATH: str = os.getenv("DB_PATH", "kei.db")
DEV_GUILD_IDS: list[int] = [
    int(gid.strip())
    for gid in os.getenv("DEV_GUILD_IDS", "").split(",")
    if gid.strip()
]

# 포인트 설정
BASE_POINTS: int = 10
STREAK_BONUS_POINTS: int = 50
STREAK_BONUS_INTERVAL: int = 7  # 7일마다 보너스
