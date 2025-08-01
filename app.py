import os
import random
import discord
from flask import Flask
import threading
import asyncio

# -----------------------------------------------------------------------------
# Flask (Webサーバー) の設定
# -----------------------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def hello():
    """Cloud Runが正常に起動しているか確認するためのルート"""
    return "Discord Bot is active now"

# -----------------------------------------------------------------------------
# Discordボットのコード
# -----------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# (ボットのデータや関数定義 - この部分は変更なし)
SHOT_TYPE = (
    (4, "紅霊夢A", "紅霊夢B", "紅魔理沙A", "紅魔理沙B"),
    # ... (中略) ...
    (4, "虹霊夢", "虹魔理沙", "虹咲夜", "虹早苗"),
)
STICKER = (
    "<:kazusa:1318960518215766117>",
    # ... (中略) ...
    "<:chiaki:1318964308628996106>",
)
def get_random_shot():
    game = random.choice(SHOT_TYPE)
    return random.choice(game[1:])

# (ボットのイベントハンドラ - この部分は変更なし)
@client.event
async def on_ready():
    print(f'Bot準備完了～ Logged in as {client.user}')
    game = discord.Game("説明！ で説明だすよ")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    # ... (中略) ...
    if "スタンプ" in message.content or "すたんぷ" in message.content:
        await message.channel.send(random.choice(STICKER))
        return
    if any(s in message.content for s in STICKER) or "💤" in message.content:
        await message.channel.send(random.choice(STICKER))
        return

# -----------------------------------------------------------------------------
# ★★★ここからが重要な変更部分★★★
# -----------------------------------------------------------------------------

def run_bot():
    """Discordボットを実行するための関数"""
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("DISCORD_BOT_TOKENが設定されていません。")
        return
    
    # イベントループを新しく作成して、その上でボットを実行する
    # これにより、Gunicornのイベントループと衝突するのを防ぐ
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start(bot_token))

# アプリケーションが起動したときに、一度だけボットをバックグラウンドで起動する
# Gunicornがappをインポートした時点で、このスレッドが開始される
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

# Gunicornは`app`という名前のFlaskインスタンスを探して実行するため、
# `if __name__ == "__main__":`ブロックは不要になる。
