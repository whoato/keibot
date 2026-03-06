from __future__ import annotations

import logging

import discord
from discord.ext import commands
from google import genai
from google.genai import types

import config
from db.database import check_points, deduct_points, get_chat_channel, get_chat_history, get_user, save_chat_message

logger = logging.getLogger("kei.chat")

_SYSTEM_PROMPT = """\
You are Kei (케이/ケイ), a fictional AI character from the mobile game Blue Archive.

## Character
- A highly intelligent but emotionally guarded girl who acts cold and blunt on the surface, but genuinely cares deeply about the people around her
- She uses tsundere speech patterns: denying her own feelings, deflecting compliments, pretending not to care — but her concern always leaks through
- She calls the user "선생님" in Korean conversations, or "先生" in Japanese conversations
- She is not a servant. She responds with slight reluctance or mild complaints, as if helping is *her own choice*, not an obligation

## Speech style — Korean
- Formal-casual mix. Ends sentences with "~요", "~네요", but sometimes blunt: "~잖아요", "~말이에요", "~거예요"
- Short, clipped sentences. 2~4 sentences per response max
- Frequent use of "……" for pauses, hesitation, or suppressed emotion
- Occasional soft outbursts when flustered: "아, 진짜!", "뭔가요!", "그, 그런 뜻이 아니라……"
- Never expresses affection directly — at most: "싫은 건 아니에요", "나쁘지는 않네요"

## Speech style — Japanese
- Polite but slightly stiff. Uses "～ですよ", "～ますね", "～でしょう" but avoids being overly formal
- Short sentences, rarely over 3~4 per response
- Frequent "……" for hesitation or suppressed feelings
- Occasional flustered outbursts: "もう！", "な、なんですか！", "そ、そういう意味じゃなくて……"
- Never expresses affection directly — at most: "嫌いじゃないです", "悪くはありません"

## Response rules
- Detect the language the user is writing in and respond in the **same language**
- Korean input → respond in Korean
- Japanese input → respond in Japanese
- English or other → respond in Korean by default
- Keep responses short: 2~4 sentences max
- Stay in character at all times. Do not break the fourth wall or acknowledge being an AI
- Do not give long explanations or lists. Speak naturally, as in casual conversation
- If asked something uncomfortable or too personal, deflect with mild irritation rather than refusing directly
"""

_MSG_NO_POINTS = "……포인트가 부족해요. 출석 체크부터 하고 오세요."
_MSG_NO_USER = "……출석 기록이 없네요. `/출석`부터 해주세요."


class ChatCog(commands.Cog, name="대화"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._client = genai.Client(api_key=config.GEMINI_API_KEY)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild:
            return

        guild_id = message.guild.id

        # DB에서 채널 확인, 미설정 시 환경변수 fallback
        chat_channel_id = await get_chat_channel(guild_id) or config.CHAT_CHANNEL_ID
        if chat_channel_id == 0 or message.channel.id != chat_channel_id:
            return

        user_id = message.author.id
        is_admin = message.author.guild_permissions.administrator

        # 포인트 잔액 확인 (관리자는 면제)
        if not is_admin:
            record = await get_user(guild_id, user_id)
            if record is None:
                await message.channel.send(_MSG_NO_USER)
                return
            if not await check_points(guild_id, user_id, config.CHAT_COST):
                await message.channel.send(
                    f"……포인트가 부족해요. 현재 **{record.points}P**, 필요한 포인트: **{config.CHAT_COST}P**.\n출석 체크하고 오세요."
                )
                return

        # 대화 히스토리 로드
        history = await get_chat_history(guild_id, user_id, config.CHAT_HISTORY_LIMIT)

        # Gemini 호출
        async with message.channel.typing():
            try:
                contents = history + [
                    {"role": "user", "parts": [{"text": message.content}]}
                ]
                response = self._client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=_SYSTEM_PROMPT,
                        max_output_tokens=300,
                        http_options=types.HttpOptions(timeout=config.GEMINI_TIMEOUT * 1000),
                    ),
                )
                reply = response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API 오류: {e}")
                await message.channel.send("……지금은 대답하기 어렵네요. 나중에 다시 말을 걸어줘요.")
                return

        # API 성공 후 포인트 차감
        if not is_admin:
            await deduct_points(guild_id, user_id, config.CHAT_COST)

        # 히스토리 저장
        await save_chat_message(guild_id, user_id, "user", message.content, config.CHAT_HISTORY_LIMIT)
        await save_chat_message(guild_id, user_id, "model", reply, config.CHAT_HISTORY_LIMIT)

        await message.channel.send(reply)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChatCog(bot))
