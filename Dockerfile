# Pythonの公式イメージをベースにする
FROM python:3.10-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app

# requirements.txtを先にコピーしてライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# GunicornでFlaskアプリを起動するコマンド
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
