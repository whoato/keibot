from __future__ import annotations

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands


def _get_greeting(hour: int) -> str:
    if 5 <= hour < 12:
        return (
            "……아침부터 부르는 건가요, 선생님.\n"
            "뭐, 딱히 싫다는 건 아니지만요. 식사는 제때 하시는 거죠?\n"
            "과로는 적당히. 그렇다고 늘어지는 것도 적당히. ……정말, 못미덥다니까요."
        )
    elif 12 <= hour < 18:
        return (
            "왜요. 아무 일 없으면 부르지 마세요.\n"
            "……네? 제가 무사히 잘 있는 걸 보는 게 일이라고요?\n"
            "진짜, 이 어른 못하는 말이 없네요! ……뭐. 아픈 곳 없죠? 좋아요. 다행이네요."
        )
    elif 18 <= hour < 22:
        return (
            "……오늘도 수고하셨어요, 선생님.\n"
            "수고했다고 말하는 건 아니에요. 당연한 걸 한 것뿐이니까요.\n"
            "뭐, 그래도…… 이렇게 있을 수 있다는 건, 확실히 좋네요."
        )
    else:
        return (
            "……선생님. 이 시간에 아직 안 주무신 건가요.\n"
            "휴식, 잊지 마세요. 양치질도요.\n"
            "너무 위험한 일은 하지 마세요. 선생님이 없어지는 건…… 저도, 싫으니까요……"
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
