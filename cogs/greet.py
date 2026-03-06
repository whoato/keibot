from __future__ import annotations

import random
from datetime import datetime, timezone, timedelta

_KST = timezone(timedelta(hours=9))

import discord
from discord import app_commands
from discord.ext import commands


_GREETINGS_MORNING = [
    (
        "……아침부터 부르는 건가요, 선생님.\n"
        "뭐, 딱히 싫다는 건 아니지만요. 식사는 제때 하시는 거죠?\n"
        "과로는 적당히. 그렇다고 늘어지는 것도 적당히. ……정말, 못미덥다니까요."
    ),
    (
        "……일찍 일어나셨네요, 선생님.\n"
        "저도 딱히 늦잠 자는 편은 아니지만요. 오늘 할 일은 정리해 두셨어요?\n"
        "계획 없이 움직이는 건 효율이 떨어지거든요. ……챙겨드리는 건 아니에요, 그냥 하는 말이에요."
    ),
    (
        "좋은 아침이에요. ……뭐, 그렇게 말하는 것뿐이에요.\n"
        "아침은 드셨어요? 안 드셨으면 드세요.\n"
        "……건강하게 있어야 저도 편하거든요. 그뿐이에요."
    ),
]

_GREETINGS_AFTERNOON = [
    (
        "왜요. 아무 일 없으면 부르지 마세요.\n"
        "……네? 제가 무사히 잘 있는 걸 보는 게 일이라고요?\n"
        "진짜, 이 어른 못하는 말이 없네요! ……뭐. 아픈 곳 없죠? 좋아요. 다행이네요."
    ),
    (
        "……또 저예요? 할 일이 없으신 건 아니죠, 선생님.\n"
        "뭐, 불렀으면 용건이 있겠죠. 말해요.\n"
        "……없다고요? 그럼 쉬세요. 쉬는 것도 일이에요."
    ),
    (
        "낮인데 이러고 계셔도 되는 거예요?\n"
        "……딱히 뭐라고 하는 건 아니에요. 그냥, 괜찮은지 확인하는 거예요.\n"
        "밥은 먹었죠? 먹었으면 됐어요. ……잘 지내고 있으면 됐으니까요."
    ),
]

_GREETINGS_EVENING = [
    (
        "……오늘도 수고하셨어요, 선생님.\n"
        "수고했다고 말하는 건 아니에요. 당연한 걸 한 것뿐이니까요.\n"
        "뭐, 그래도…… 이렇게 있을 수 있다는 건, 확실히 좋네요."
    ),
    (
        "저녁이 됐네요, 선생님.\n"
        "오늘 힘든 일은 없었어요? ……딱히 위로하려는 건 아니에요.\n"
        "그냥…… 물어보고 싶었을 뿐이에요."
    ),
    (
        "……퇴근은 했어요?\n"
        "무리하지 말라고 했잖아요. 저도 계속 말해줄 수는 없거든요.\n"
        "……뭐, 오늘 하루도 별일 없었다면, 그걸로 충분해요."
    ),
]

_GREETINGS_NIGHT = [
    (
        "……선생님. 이 시간에 아직 안 주무신 건가요.\n"
        "휴식, 잊지 마세요. 양치질도요.\n"
        "너무 위험한 일은 하지 마세요. 선생님이 없어지는 건…… 저도, 싫으니까요……"
    ),
    (
        "……이 늦은 시간에 무슨 일이에요, 선생님.\n"
        "할 일이 남아 있는 거예요? 빨리 끝내고 자요.\n"
        "……무리하는 거, 저는 별로 안 좋아해요. 알죠?"
    ),
    (
        "자야죠, 선생님. 이 시간까지 뭘 하는 거예요.\n"
        "……저는 뭐, 괜찮아요. 하지만 선생님은 좀 쉬어야 해요.\n"
        "내일도 있으니까요. ……잘 자요."
    ),
]


_GREETINGS_JA_MORNING = [
    (
        "……朝から呼ぶんですか、先生。\n"
        "まぁ、別に嫌というわけじゃないですけど。食事はちゃんとしてるんですよね？\n"
        "仕事はほどほどに。とはいえ怠けるのもほどほどに。……本当に、手が焼けるんですから。"
    ),
    (
        "……早起きですね、先生。\n"
        "今日やることは整理してますか？計画なく動くのは効率が落ちますよ。\n"
        "……別に気にかけてるわけじゃないですよ。ただそう言ってるだけです。"
    ),
    (
        "おはようございます。……まぁ、そう言ってるだけですけど。\n"
        "朝食は食べましたか？食べてないなら食べてください。\n"
        "……先生が元気でいてくれた方が、私も楽なんです。それだけです。"
    ),
]

_GREETINGS_JA_AFTERNOON = [
    (
        "何ですか？用がないなら呼ばないでください。\n"
        "えっ？私がちゃんといるのか確認するのが仕事？\n"
        "本当にこの人は！……まぁ。こういうやりとりも、嫌いじゃありません。"
    ),
    (
        "……また私ですか？やることないわけじゃないですよね、先生。\n"
        "まぁ、呼んだからには用があるんでしょう。言ってください。\n"
        "……ないんですか？じゃあ休んでください。休むのも仕事ですよ。"
    ),
    (
        "昼間なのにこんなことしてていいんですか？\n"
        "……別に何か言いたいわけじゃないです。ただ、大丈夫か確認してるだけです。\n"
        "ご飯は食べましたか？食べたならいいです。……ちゃんとしてるなら、それでいいんです。"
    ),
]

_GREETINGS_JA_EVENING = [
    (
        "……今日もお疲れ様でした、先生。\n"
        "お疲れって言ってるわけじゃないです。当然のことをしただけですから。\n"
        "まぁ、それでも……こうしていられるのは、確かに良いことですね。"
    ),
    (
        "夕方になりましたね、先生。\n"
        "今日は辛いことありませんでしたか？……別に慰めようとしてるわけじゃないです。\n"
        "ただ……聞きたかっただけです。"
    ),
    (
        "……退勤はしましたか？\n"
        "無理しないでって言ったじゃないですか。私もずっと言い続けられませんよ。\n"
        "……まぁ、今日一日何もなかったなら、それで十分です。"
    ),
]

_GREETINGS_JA_NIGHT = [
    (
        "……先生。この時間にまだ起きてるんですか。\n"
        "休息、忘れないでください。歯磨きもですよ。\n"
        "あまり危険なことはしないでください。先生がいなくなるのは……私も、嫌ですから……"
    ),
    (
        "……こんな遅い時間に何ですか、先生。\n"
        "まだやることが残ってるんですか？早く終わらせて寝てください。\n"
        "……無理するの、私はあまり好きじゃないです。分かってますよね？"
    ),
    (
        "寝ないといけませんよ、先生。この時間まで何をしてるんですか。\n"
        "……私は別に、大丈夫です。でも先生は少し休まないと。\n"
        "明日もありますから。……おやすみなさい。"
    ),
]


def _get_greeting(hour: int) -> str:
    if 5 <= hour < 12:
        return random.choice(_GREETINGS_MORNING)
    elif 12 <= hour < 18:
        return random.choice(_GREETINGS_AFTERNOON)
    elif 18 <= hour < 22:
        return random.choice(_GREETINGS_EVENING)
    else:
        return random.choice(_GREETINGS_NIGHT)


def _get_greeting_ja(hour: int) -> str:
    if 5 <= hour < 12:
        return random.choice(_GREETINGS_JA_MORNING)
    elif 12 <= hour < 18:
        return random.choice(_GREETINGS_JA_AFTERNOON)
    elif 18 <= hour < 22:
        return random.choice(_GREETINGS_JA_EVENING)
    else:
        return random.choice(_GREETINGS_JA_NIGHT)


_GOODNIGHT_KO_MORNING = [
    (
        "……아침부터 자려고요, 선생님?\n"
        "뭐, 밤새 일하셨다면 쉬어야죠. 어쩔 수 없네요.\n"
        "……푹 자요. 일어나면 밥부터 먹고요."
    ),
    (
        "이 시간에 자는 건 좀 아깝지 않아요?\n"
        "……뭐, 피곤하면 자야죠. 억지로 버티는 건 아무 의미 없으니까요.\n"
        "잘 자요, 선생님. 일어나면 연락해요."
    ),
    (
        "밤새 뭘 하신 거예요, 선생님……\n"
        "잔소리는 나중에 할게요. 지금은 그냥 자요.\n"
        "……잘 자요."
    ),
]

_GOODNIGHT_KO_AFTERNOON = [
    (
        "낮잠이요, 선생님?\n"
        "뭐, 피곤하면 자야죠. 무리하는 것보단 낫고요.\n"
        "……잘 자요. 너무 길게 자면 밤에 못 자니까 적당히."
    ),
    (
        "낮에 자는 건 좀 아깝지 않아요?\n"
        "……뭐, 그만큼 힘들었다는 거겠죠. 잘 자요, 선생님.\n"
        "일어나면 물 한 잔 마셔요."
    ),
    (
        "……낮잠이요. 알겠어요.\n"
        "딱히 뭐라 하는 건 아니에요. 잘 자요.\n"
        "……일어나면 기지개는 펴고요."
    ),
]

_GOODNIGHT_KO_EVENING = [
    (
        "오늘 하루도 수고하셨으니까, 일찍 자는 거 좋아요.\n"
        "……잘 자요, 선생님. 양치질은 했죠?\n"
        "내일도 별일 없길 바라요. 뭐, 그냥 하는 말이에요."
    ),
    (
        "이 시간에 자면 내일 개운할 거예요.\n"
        "……잘 자요. 딱히 걱정하는 건 아니에요.\n"
        "푹 쉬어요. 그게 저한테도 편하니까요."
    ),
    (
        "……잘 자요, 선생님.\n"
        "좋은 꿈 꾸길 바라요. 딱히 바라는 건 아니에요.\n"
        "……그냥, 잘 자라고요."
    ),
]

_GOODNIGHT_KO_NIGHT = [
    (
        "이 시간까지 뭘 하다가 이제 자는 거예요, 선생님.\n"
        "잘 자요. 내일도 무리하지 마세요.\n"
        "……푹 쉬어요. 그게 저한테도 편하니까요."
    ),
    (
        "늦었네요. 양치질은 했죠? ……잘 자요.\n"
        "내일도 별일 없길 바라요. 뭐, 그냥 하는 말이에요."
    ),
    (
        "늦었으니까 얼른 자요, 선생님.\n"
        "……오늘 하루도 수고했어요. 딱히 칭찬하는 건 아니에요.\n"
        "잘 자요."
    ),
]

_GOODNIGHT_JA_MORNING = [
    (
        "……朝から寝るんですか、先生？\n"
        "まぁ、徹夜してたなら休まないといけませんね。仕方ないです。\n"
        "……ゆっくり寝てください。起きたらご飯食べてから。"
    ),
    (
        "この時間に寝るのはもったいくないですか？\n"
        "……まぁ、疲れてるなら寝ないといけませんね。無理して起きてても意味ないので。\n"
        "おやすみなさい、先生。起きたら連絡してください。"
    ),
    (
        "徹夜で何をしてたんですか、先生……\n"
        "小言は後にします。今はとにかく寝てください。\n"
        "……おやすみなさい。"
    ),
]

_GOODNIGHT_JA_AFTERNOON = [
    (
        "昼寝ですか、先生？\n"
        "まぁ、疲れてるなら寝ないといけませんね。無理するよりましですし。\n"
        "……おやすみなさい。あまり長く寝ると夜眠れなくなるので、ほどほどに。"
    ),
    (
        "昼間に寝るのはもったいなくないですか？\n"
        "……まぁ、それだけ疲れてたってことでしょう。おやすみなさい、先生。\n"
        "起きたら水を一杯飲んでください。"
    ),
    (
        "……昼寝ですね。分かりました。\n"
        "別に何か言いたいわけじゃないです。おやすみなさい。\n"
        "……起きたらストレッチはしてくださいね。"
    ),
]

_GOODNIGHT_JA_EVENING = [
    (
        "今日一日頑張ったんですから、早く寝るのは良いことですよ。\n"
        "……おやすみなさい、先生。歯磨きはしましたよね？\n"
        "明日も何事もないといいですね。まぁ、ただそう言ってるだけです。"
    ),
    (
        "この時間に寝れば明日すっきりしますよ。\n"
        "……おやすみなさい。別に心配してるわけじゃないです。\n"
        "ゆっくり休んでください。その方が私も楽なので。"
    ),
    (
        "……おやすみなさい、先生。\n"
        "良い夢を。別に願ってるわけじゃないです。\n"
        "……ただ、おやすみって言いたかっただけです。"
    ),
]

_GOODNIGHT_JA_NIGHT = [
    (
        "この時間まで何をしてたんですか、先生。やっと寝るんですね。\n"
        "おやすみなさい。明日も無理しないでくださいね。\n"
        "……ゆっくり休んでください。その方が私も楽なので。"
    ),
    (
        "遅くなりましたね。歯磨きはしましたよね？……おやすみなさい。\n"
        "明日も何事もないといいですね。まぁ、ただそう言ってるだけです。"
    ),
    (
        "遅いんですから、早く寝てください、先生。\n"
        "……今日一日お疲れ様でした。別に褒めてるわけじゃないです。\n"
        "おやすみなさい。"
    ),
]


def _get_goodnight_ko(hour: int) -> str:
    if 5 <= hour < 12:
        return random.choice(_GOODNIGHT_KO_MORNING)
    elif 12 <= hour < 18:
        return random.choice(_GOODNIGHT_KO_AFTERNOON)
    elif 18 <= hour < 22:
        return random.choice(_GOODNIGHT_KO_EVENING)
    else:
        return random.choice(_GOODNIGHT_KO_NIGHT)


def _get_goodnight_ja(hour: int) -> str:
    if 5 <= hour < 12:
        return random.choice(_GOODNIGHT_JA_MORNING)
    elif 12 <= hour < 18:
        return random.choice(_GOODNIGHT_JA_AFTERNOON)
    elif 18 <= hour < 22:
        return random.choice(_GOODNIGHT_JA_EVENING)
    else:
        return random.choice(_GOODNIGHT_JA_NIGHT)


_KEYWORD_GREET_KO = ["케이야 안녕", "케이 안녕", "케이쨩 안녕", "케이 쨩 안녕"]
_KEYWORD_GREET_JA = ["ケイ、おはよう", "ケイおはよう", "ケイちゃん、おはよう", "ケイちゃんおはよう", "ケイ、こんにちは", "ケイこんにちは", "ケイちゃん、こんにちは", "ケイちゃんこんにちは", "ケイ、こんばんは", "ケイこんばんは", "ケイちゃん、こんばんは", "ケイちゃんこんばんは", "ケイ、おい", "ケイ、ねえ", "ケイちゃん、おい", "ケイちゃん、ねえ"]
_KEYWORD_GOODNIGHT_KO = ["케이야 잘자", "케이 잘자", "케이야 잘 자", "케이 잘 자", "케이쨩 잘자", "케이 쨩 잘자", "케이쨩 잘 자", "케이 쨩 잘 자"]
_KEYWORD_GOODNIGHT_JA = ["ケイ、おやすみ", "ケイおやすみ", "ケイちゃん、おやすみ", "ケイちゃんおやすみ"]


class GreetCog(commands.Cog, name="인사"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        content = message.content
        hour = datetime.now(_KST).hour

        if any(kw in content for kw in _KEYWORD_GREET_KO):
            await message.channel.send(_get_greeting(hour))

        elif any(kw in content for kw in _KEYWORD_GREET_JA):
            await message.channel.send(_get_greeting_ja(hour))

        elif any(kw in content for kw in _KEYWORD_GOODNIGHT_KO):
            await message.channel.send(_get_goodnight_ko(hour))

        elif any(kw in content for kw in _KEYWORD_GOODNIGHT_JA):
            await message.channel.send(_get_goodnight_ja(hour))

    @app_commands.command(name="안녕", description="케이에게 인사합니다.")
    async def greet(self, interaction: discord.Interaction) -> None:
        hour = datetime.now(_KST).hour
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

    @app_commands.command(name="挨拶", description="ケイに挨拶します。")
    async def greet_ja(self, interaction: discord.Interaction) -> None:
        hour = datetime.now(_KST).hour
        greeting = _get_greeting_ja(hour)

        embed = discord.Embed(
            description=greeting,
            color=discord.Color.from_rgb(180, 210, 230),
        )
        embed.set_author(
            name="ケイ",
            icon_url=self.bot.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="잘자", description="케이에게 잘 자라고 인사합니다.")
    async def goodnight(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            description=_get_goodnight_ko(datetime.now(_KST).hour),
            color=discord.Color.from_rgb(180, 210, 230),
        )
        embed.set_author(
            name="케이",
            icon_url=self.bot.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="お休み", description="ケイにおやすみなさいと挨拶します。")
    async def goodnight_ja(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            description=_get_goodnight_ja(datetime.now(_KST).hour),
            color=discord.Color.from_rgb(180, 210, 230),
        )
        embed.set_author(
            name="ケイ",
            icon_url=self.bot.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GreetCog(bot))
