from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from db import database


class AdminCog(commands.Cog, name="관리자"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="출석초기화", description="[관리자] 특정 선생님의 출석 데이터를 초기화합니다.")
    @app_commands.describe(member="초기화할 유저를 선택하세요.")
    @app_commands.default_permissions(administrator=True)
    async def reset_attendance(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        success = await database.reset_user(interaction.guild_id, member.id)

        if not success:
            embed = discord.Embed(
                title="초기화 실패",
                description=f"{member.mention}님의 출석 기록이 존재하지 않습니다.",
                color=discord.Color.red(),
            )
        else:
            embed = discord.Embed(
                title="초기화 완료",
                description=f"{member.mention}님의 출석 데이터가 초기화되었습니다.",
                color=discord.Color.green(),
            )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
