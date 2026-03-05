import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]
GUILD_ID: int = int(os.environ["GUILD_ID"])
DB_PATH: str = os.getenv("DB_PATH", "kei.db")

# 포인트 설정
BASE_POINTS: int = 10
STREAK_BONUS_POINTS: int = 50
STREAK_BONUS_INTERVAL: int = 7  # 7일마다 보너스
