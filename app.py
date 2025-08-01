import os
import random
import discord
from flask import Flask, request
import threading

# Flaskアプリケーションの準備 (Cloud Runを正常に保つため)
app = Flask(__name__)

@app.route('/')
def hello():
    """Cloud Runが正常に起動していることを確認するためのルート"""
    return "Discord Bot is active now"

def run_flask_app():
    """Flaskアプリを別スレッドで実行する関数"""
    # Gunicornが動かすため、ポートは環境変数から取得
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# -----------------------------------------------------------------------------
# Discordボットのコード
# -----------------------------------------------------------------------------

# JavaScriptのデータ構造をPythonのリスト（List）とタプル（Tuple）で再現
SHOT_TYPE = (
    (4, "紅霊夢A", "紅霊夢B", "紅魔理沙A", "紅魔理沙B"),
    (6, "妖霊夢A", "妖霊夢B", "妖魔理沙A", "妖魔理沙B", "妖咲夜A", "妖咲夜B"),
    (12, "永結界", "永幽冥", "永詠唱", "永紅魔", "永霊夢", "永紫", "永妖夢", "永幽々子", "永魔理沙", "永アリス", "永咲夜", "永レミリア"),
    (6, "風霊夢A", "風霊夢B", "風霊夢C", "風魔理沙A", "風魔理沙B", "風魔理沙C"),
    (6, "地霊夢A", "地霊夢B", "地霊夢C", "地魔理沙A", "地魔理沙B", "地魔理沙C"),
    (6, "星霊夢A", "星霊夢B", "星魔理沙A", "星魔理沙B", "星早苗A", "星早苗B"),
    (4, "神霊夢", "神魔理沙", "神早苗", "神妖夢"),
    (6, "輝霊夢A", "輝霊夢B", "輝魔理沙A", "輝魔理沙B", "輝咲夜A", "輝咲夜B"),
    (4, "紺霊夢", "紺魔理沙", "紺早苗", "紺鈴仙"),
    (16, "春春", "春夏", "春秋", "春冬", "夏春", "夏夏", "夏秋", "夏冬", "秋春", "秋夏", "秋秋", "秋冬", "冬春", "冬夏", "冬秋", "冬冬"),
    (9, "霊夢W", "霊夢E", "霊夢O", "魔理沙W", "魔理沙E", "魔理沙O", "妖夢W", "妖夢E", "妖夢O"),
    (4, "虹霊夢", "虹魔理沙", "虹咲夜", "虹早苗"),
)

# カスタム絵文字やステッカー
STICKER = (
    "<:kazusa:1318960518215766117>",
    "<:plana1:1318960569822351370>",
    "<:plana:1318960622268059728>",
    "<:nyny:1318960704249663498>",
    "<:plana2:1318964188537815150>",
    "<:usio:1318964272038019132>",
    "<:chiaki:1318964308628996106>",
)

# discord.pyのクライアントを作成
intents = discord.Intents.default()
intents.message_content = True # メッセージの内容を読み取るために必要
client = discord.Client(intents=intents)

def get_random_shot():
    """ランダムな機体を抽選する関数"""
    game = random.choice(SHOT_TYPE)
    # 最初の要素は機体数なので、それ以降の要素からランダムに選ぶ
    return random.choice(game[1:])

@client.event
async def on_ready():
    """ボットが準備完了したときに実行されるイベント"""
    print(f'Bot準備完了～ Logged in as {client.user}')
    # アクティビティの設定
    game = discord.Game("説明！ で説明だすよ")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    """メッセージが投稿されたときに実行されるイベント"""
    # 自分のメッセージや他のBotのメッセージは無視
    if message.author == client.user or message.author.bot:
        return
    
    # 自分へのメンション、または特定のキーワードに反応
    if (client.user.mentioned_in(message) or
        "本日の機体" in message.content or
        "今日の機体" in message.content or
        "きょうのきたい" in message.content or
        "ほんじつのきたい" in message.content or
        "イッツルナティックターイム！" in message.content):
        await message.channel.send(get_random_shot())
        return

    # リンクの置換
    if "x.com" in message.content:
        await message.channel.send(message.content.replace("x.com", "vxtwitter.com"))
        return
    if "www.pixiv.net" in message.content:
        await message.channel.send(message.content.replace("www.pixiv.net", "www.phixiv.net"))
        return

    # 特定の単語への応答
    if "にゃ～ん" in message.content or "にゃーん" in message.content:
        await message.channel.send("にゃ～ん")
        return
    if "説明!" in message.content or "せつめい!" in message.content:
        await message.channel.send("今日の機体、本日の機体 またはメンションで機体出します")
        return
    if "ソースコード" in message.content or "そーす" in message.content:
        await message.channel.send("https://glitch.com/edit/#!/play-tohou?path=server.js%3A149%3A28")
        return

    # スタンプへの応答
    if "スタンプ" in message.content or "すたんぷ" in message.content:
        await message.channel.send(random.choice(STICKER))
        return
    
    # カスタム絵文字が含まれていたらランダムなスタンプで応答
    if any(s in message.content for s in STICKER) or "💤" in message.content:
        await message.channel.send(random.choice(STICKER))
        return

# -----------------------------------------------------------------------------
# 実行部分
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # ボットトークンが設定されていなければ終了
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("DISCORD_BOT_TOKENが設定されていません。")
        exit()

    # Flaskアプリをバックグラウンドで起動
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Discordボットを起動
    client.run(bot_token)
