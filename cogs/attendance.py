from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import config
from db import database


class AttendanceCog(commands.Cog, name="출석"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="출석", description="오늘 출석 체크를 합니다.")
    async def attend(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=False)

        result = await database.attend(
            user_id=interaction.user.id,
            username=interaction.user.display_name,
        )

        if result.already_attended:
            embed = discord.Embed(
                title="이미 출석했습니다",
                description="오늘은 이미 출석 체크를 완료했습니다. 내일 다시 출석해 주세요!",
                color=discord.Color.orange(),
            )
            await interaction.followup.send(embed=embed)
            return

        user = result.user
        desc = f"**+{result.points_earned} 포인트** 획득!"

        if result.is_streak_bonus:
            desc += f"\n**연속 {result.streak}일 보너스! +{config.STREAK_BONUS_POINTS} 포인트 추가 지급!**"

        desc += f"\n\n현재 포인트: **{user.points}**\n연속 출석: **{result.streak}일**\n총 출석: **{user.total_days}일**"

        embed = discord.Embed(
            title=f"{interaction.user.display_name}님, 출석 완료!",
            description=desc,
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="내정보", description="내 출석 현황을 확인합니다.")
    async def my_info(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        user = await database.get_user(interaction.user.id)

        if user is None:
            embed = discord.Embed(
                title="출석 기록 없음",
                description="/출석 명령어로 출석 체크를 시작해 보세요!",
                color=discord.Color.blurple(),
            )
            await interaction.followup.send(embed=embed)
            return

        last = user.last_attend.isoformat() if user.last_attend else "없음"
        embed = discord.Embed(
            title=f"{interaction.user.display_name}님의 출석 정보",
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="총 포인트", value=f"**{user.points}**", inline=True)
        embed.add_field(name="연속 출석", value=f"**{user.streak}일**", inline=True)
        embed.add_field(name="총 출석일", value=f"**{user.total_days}일**", inline=True)
        embed.add_field(name="마지막 출석", value=last, inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="랭킹", description="서버 출석 랭킹 상위 10명을 확인합니다.")
    async def ranking(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=False)

        users = await database.get_ranking(limit=10)

        if not users:
            embed = discord.Embed(
                title="출석 랭킹",
                description="아직 출석한 유저가 없습니다.",
                color=discord.Color.gold(),
            )
            await interaction.followup.send(embed=embed)
            return

        medals = ["1", "2", "3"]
        lines = []
        for i, u in enumerate(users, start=1):
            rank = medals[i - 1] if i <= 3 else str(i)
            lines.append(f"`{rank}.` **{u.username}** — {u.total_days}일 출석 / {u.points}P / {u.streak}일 연속")

        embed = discord.Embed(
            title="출석 랭킹 TOP 10",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AttendanceCog(bot))
