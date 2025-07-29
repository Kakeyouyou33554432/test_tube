# Pythonの公式イメージをベースにする
FROM python:3.10-slim

# ffmpegをインストール
RUN apt-get update && apt-get install -y ffmpeg

# 環境変数を設定 (Gunicornのワーカー数など)
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

# 必要なファイルをコピー
COPY requirements.txt .

# Pythonライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# アプリケーションを実行
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
