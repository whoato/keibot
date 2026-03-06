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
    def __init__(self, sync: bool = False, clear_global: bool = False) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self._sync = sync
        self._clear_global = clear_global

    async def setup_hook(self) -> None:
        await init_db()
        logger.info("DB 초기화 완료")

        for cog in COGS:
            await self.load_extension(cog)
            logger.info(f"Cog 로드: {cog}")

        if self._clear_global:
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            logger.info("글로벌 슬래시 커맨드 전체 삭제 완료 (최대 1시간 소요)")

        if self._sync:
            if config.DEV_GUILD_IDS:
                for guild_id in config.DEV_GUILD_IDS:
                    guild = discord.Object(id=guild_id)
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync(guild=guild)
                    logger.info(f"슬래시 커맨드 길드 동기화 완료 (즉시 반영, 길드: {guild_id})")
            else:
                await self.tree.sync()
                logger.info("슬래시 커맨드 글로벌 동기화 완료 (최대 1시간 소요)")
        elif not self._clear_global:
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
    clear_global = "--clear-global" in sys.argv
    async with Kei(sync=sync, clear_global=clear_global) as bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
