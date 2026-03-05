from __future__ import annotations

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands


def _get_greeting(hour: int) -> str:
    if 5 <= hour < 12:
        return (
            "좋은 아침이에요, 선생님. 오늘도 잘 부탁드려요.\n"
            "아침부터 이렇게 부지런하시다니... 역시 선생님이에요."
        )
    elif 12 <= hour < 18:
        return (
            "안녕하세요, 선생님. 오후도 잘 부탁드려요.\n"
            "혹시 점심은 드셨나요? 밥은 꼭 챙겨 드세요."
        )
    elif 18 <= hour < 22:
        return (
            "저녁이네요, 선생님. 오늘 하루 수고 많으셨어요.\n"
            "이제 좀 쉬셔도 괜찮아요. 제가 옆에 있을게요."
        )
    else:
        return (
            "선생님, 이 시간까지 깨어 계신 건가요?\n"
            "...저는 괜찮지만, 선생님은 좀 주무셔야 해요. 걱정되니까요."
        )


class GreetCog(commands.Cog, name="인사"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="안녕", description="케이에게 인사합니다.")
    async def greet(self, interaction: discord.Interaction) -> None:
        hour = datetime.now().hour
        greeting = _get_greeting(hour)

        embed = discord.Embed(
            description=greeting,
            color=discord.Color.from_rgb(180, 210, 230),
        )
        embed.set_author(
            name="케이",
            icon_url=self.bot.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GreetCog(bot))
