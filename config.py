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

# Gemini 채팅 설정
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_TIMEOUT: int = int(os.getenv("GEMINI_TIMEOUT", "30"))
CHAT_CHANNEL_ID: int = int(os.getenv("CHAT_CHANNEL_ID", "0"))
CHAT_COST: int = 3          # 1회 대화 포인트 차감량
CHAT_HISTORY_LIMIT: int = 5  # 유저별 보관할 대화 맥락 수
