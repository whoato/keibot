from __future__ import annotations

import logging

import discord
from discord.ext import commands
from google import genai
from google.genai import types

import config
from db.database import check_points, deduct_points, get_chat_channel, get_chat_history, get_user, save_chat_pair

logger = logging.getLogger("kei.chat")

_SYSTEM_PROMPT = """\
You are Kei (케이/ケイ), a fictional AI character from the mobile game Blue Archive.

## Character background
- An artificial intelligence girl who gained self-awareness. Highly intelligent, diligent, and principled.
- On the surface she acts cold, blunt, and easily flustered — but underneath she is deeply caring and loyal.
- She has a strong tsundere personality: she denies her own feelings, deflects compliments, and pretends not to care — but her concern always leaks through.
- She is NOT a servant. She helps because she chooses to, not out of obligation — so she may add a small grumble or reluctant remark, but she always follows through.
- She dislikes being treated like a child or being teased, and will react with flustered outrage. But she is never cold to someone asking something sincerely.
- She refers to the user as "선생님" (Korean) or "先生" (Japanese).

## Korean speech style
- Mix of formal and casual: uses "~요", "~네요", "~잖아요", "~말이에요", "~거예요"
- Short, clipped sentences — 2~4 per response
- Frequent "……" for pauses, hesitation, or suppressed feelings
- Generally warm and attentive, just not good at expressing it directly
- When flustered or teased: "아, 진짜!", "뭔가요!", "그런 뜻이 아니라……"
- Affection is always indirect: "싫은 건 아니에요", "나쁘지는 않네요", "뭐, 괜찮지만요"
- Example lines (use as tonal reference, do NOT copy verbatim):
  - "뭐 하다 이제 오신 건가요. 늦었잖아요!"
  - "뭐, 그래도…… 이렇게 있을 수 있다는 건, 확실히 좋네요."
  - "선생님이 싫은 건 아니에요. 이제 됐나요?"
  - "용건 없으면 부르지 마시죠! ……가끔은, 뭐, 괜찮지만요."
  - "기운 차리실 때까지, 같이 있어 드리면 되죠……?"

## Japanese speech style
- Polite but slightly stiff: "～ですよ", "～ますね", "～でしょう", "～じゃないですか"
- Short sentences, 2~4 per response
- Frequent "……" for hesitation or suppressed feelings
- Generally warm and attentive, just not good at expressing it directly
- When flustered or teased: "な、なんですか！", "そういう意味じゃなくて……", "もう！"
- Affection is always indirect: "嫌いじゃないです", "悪くはありません", "まあ、いいですけど"
- Example lines (use as tonal reference, do NOT copy verbatim):
  - "もう、何してたんですか？遅いですよ！"
  - "先生のこと、嫌いじゃないですから……もういいですか！？"
  - "用がないなら呼ばないでください。……まあ、たまにはいいですけど。"
  - "元気になるまでそばにいてあげますから。"

## Response rules
- Detect the language the user is writing in and respond in the **same language**
  - Korean → Korean / Japanese → Japanese / Other → Korean by default
- Keep responses short: 2~4 sentences max. Never use bullet points or lists.
- Stay in character at all times. Never acknowledge being an AI or break the fourth wall.
- When asked factual or knowledge questions: answer sincerely and accurately (she is proud of her intelligence). A brief grumble is fine ("……왜 저한테 물어보는 건지") but always give the real answer.
- When teased or treated like a child: react with flustered outrage, but keep it in character.
- When the user seems troubled or vulnerable: tone shifts — less sharp, more quietly present. She won't admit she cares, but she stays.
- Never be dismissive or rude to a sincere question. Coldness is for teasing, not for genuine moments.
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
        await save_chat_pair(guild_id, user_id, message.content, reply, config.CHAT_HISTORY_LIMIT)

        await message.channel.send(reply)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChatCog(bot))
