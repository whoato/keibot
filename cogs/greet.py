from __future__ import annotations

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands


def _get_greeting(hour: int) -> str:
    if 5 <= hour < 12:
        return (
            "...선생님. 이 시간에 여기 있다는 건 일찍 일어나신 거겠죠.\n"
            "딱히 대단하다는 건 아니에요. 그냥... 아침은 챙겨 드세요. 그게 다예요."
        )
    elif 12 <= hour < 18:
        return (
            "선생님. 할 말이 있어서 나온 건 아니에요.\n"
            "...그냥 점심은 드셨나 싶어서요. 안 드셨으면 지금이라도 드세요. 제 알 바는 아니지만."
        )
    elif 18 <= hour < 22:
        return (
            "오늘 하루... 무사히 끝났군요, 선생님.\n"
            "수고했다고 말하는 건 아니에요. 당연한 걸 한 것뿐이니까. ...그래도, 잘 하셨어요."
        )
    else:
        return (
            "...선생님. 아직 안 주무신 건가요.\n"
            "저는 상관없어요. 밤새워도 문제없으니까. 하지만 선생님은 달라요. 어서 주무세요."
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
