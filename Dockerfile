# Pythonのバージョンを3.11-slimに固定する
FROM python:3.11-slim

# 環境変数の設定
ENV PYTHONUNBUFFERED True
WORKDIR /app

# 依存関係ファイルを先にコピー
COPY requirements.txt .

# ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# アプリケーションを実行するコマンド
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
