# Pythonの公式イメージをベースにする
FROM python:3.10-slim

# ffmpegをインストール
RUN apt-get update && apt-get install -y ffmpeg

# 環境変数を設定
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

# 必要なファイルをコピー
COPY requirements.txt .

# Pythonライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ★★★ アプリケーションの実行コマンドをデバッグ用に変更 ★★★
# Gunicornではなく、Flaskの標準開発サーバーで実行します。
# これにより、より詳細なエラーログが表示されるはずです。
CMD ["python", "app.py"]
