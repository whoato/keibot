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

    @app_commands.command(name="포인트추가", description="[관리자] 특정 선생님의 포인트를 추가합니다.")
    @app_commands.describe(member="대상 유저를 선택하세요.", amount="추가할 포인트 수량 (1 이상).")
    @app_commands.default_permissions(administrator=True)
    async def add_points(
        self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1]
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        new_points = await database.adjust_points(interaction.guild_id, member.id, amount)
        if new_points is None:
            embed = discord.Embed(
                description=f"{member.mention}님의 출석 기록이 없어요.",
                color=discord.Color.red(),
            )
        else:
            embed = discord.Embed(
                description=f"{member.mention}님에게 **{amount}P** 추가했어요. (현재 **{new_points}P**)",
                color=discord.Color.green(),
            )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="포인트삭제", description="[관리자] 특정 선생님의 포인트를 차감합니다.")
    @app_commands.describe(member="대상 유저를 선택하세요.", amount="차감할 포인트 수량 (1 이상, 잔액 미만으로 차감 시 0으로 처리).")
    @app_commands.default_permissions(administrator=True)
    async def remove_points(
        self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1]
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        new_points = await database.adjust_points(interaction.guild_id, member.id, -amount)
        if new_points is None:
            embed = discord.Embed(
                description=f"{member.mention}님의 출석 기록이 없어요.",
                color=discord.Color.red(),
            )
        else:
            embed = discord.Embed(
                description=f"{member.mention}님에게서 **{amount}P** 차감했어요. (현재 **{new_points}P**)",
                color=discord.Color.orange(),
            )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="채팅채널설정", description="[관리자] 케이 AI 대화 채널을 설정합니다.")
    @app_commands.describe(channel="AI 대화를 활성화할 채널을 선택하세요.")
    @app_commands.default_permissions(administrator=True)
    async def set_chat_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        await database.set_chat_channel(interaction.guild_id, channel.id)
        embed = discord.Embed(
            description=f"{channel.mention} 채널이 케이 대화 채널로 설정됐어요.",
            color=discord.Color.from_rgb(180, 210, 230),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
