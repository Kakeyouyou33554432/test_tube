import os
import logging
import tempfile
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from google.cloud import storage
from datetime import timedelta

# ... (以前のコードの先頭部分は同じ) ...
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
# ... (以前のコードの関数定義などは同じ) ...

@app.route('/download', methods=['POST'])
def download_video():
    # ... (以前のコードと同じ) ...
    video_url = data['url']

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cookie_file_path = os.path.join(temp_dir, 'cookies.txt')

            # ★★★ここからが追加部分★★★
            try:
                # GCSからクッキーファイルをダウンロードする
                storage_client = storage.Client()
                bucket = storage_client.bucket(BUCKET_NAME)
                blob = bucket.blob('cookies.txt') # GCSにアップロードしたファイル名
                
                logging.info(f"Downloading cookies.txt from GCS to {cookie_file_path}")
                blob.download_to_filename(cookie_file_path)
                logging.info("Cookies downloaded successfully.")
                
            except Exception as e:
                logging.warning(f"Could not download cookies.txt: {e}. Proceeding without cookies.")
                cookie_file_path = None
            # ★★★ここまでが追加部分★★★

            # ... (以前のコードと同じ) ...
            
            # yt-dlpのオプションにクッキーファイルを追加
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, final_filename),
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'cookiefile': cookie_file_path # ★この行を追加
            }

            # ... (以降の処理は以前のコードと同じ) ...

# ... (以降のコードは以前のコードと同じ) ...
