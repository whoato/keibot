import asyncio
import logging

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
]


class Kei(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        await init_db()
        logger.info("DB 초기화 완료")

        for cog in COGS:
            await self.load_extension(cog)
            logger.info(f"Cog 로드: {cog}")

        guild = discord.Object(id=config.GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info(f"슬래시 커맨드 동기화 완료 (길드: {config.GUILD_ID})")

    async def on_ready(self) -> None:
        logger.info(f"케이(Kei) 봇 준비 완료 | {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="/출석 으로 출석체크",
            )
        )


async def main() -> None:
    async with Kei() as bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
