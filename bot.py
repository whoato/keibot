import asyncio
import logging
import sys

import discord
from discord.ext import commands

import config
from db.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("kei")

COGS = [
    "cogs.attendance",
    "cogs.admin",
    "cogs.greet",
]


class Kei(commands.Bot):
    def __init__(self, sync: bool = False) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self._sync = sync

    async def setup_hook(self) -> None:
        await init_db()
        logger.info("DB 초기화 완료")

        for cog in COGS:
            await self.load_extension(cog)
            logger.info(f"Cog 로드: {cog}")

        if self._sync:
            await self.tree.sync()
            logger.info("슬래시 커맨드 글로벌 동기화 완료 (최대 1시간 소요)")
        else:
            logger.info("슬래시 커맨드 동기화 생략 (sync 모드 아님)")

    async def on_ready(self) -> None:
        logger.info(f"케이(Kei) 봇 준비 완료 | {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="케이입니다.",
            )
        )


async def main() -> None:
    sync = "--sync" in sys.argv
    async with Kei(sync=sync) as bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
