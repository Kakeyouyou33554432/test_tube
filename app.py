import os
import tempfile
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from google.cloud import storage
from datetime import timedelta

app = Flask(__name__)

# 環境変数からバケット名を取得
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')

def sanitize_filename(filename, max_length=100):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '#']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:max_length]

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL not provided'}), 400
    if not BUCKET_NAME:
        return jsonify({'error': 'Server configuration error: GCS_BUCKET_NAME is not set.'}), 500

    video_url = data['url']

    try:
        # 一時的なディレクトリを作成して、その中で作業する
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'noplaylist': True,
            }

            # 動画を一時ディレクトリにダウンロード
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                downloaded_filename = ydl.prepare_filename(info_dict)
                # ファイル名をサニタイズ
                base_name = os.path.basename(downloaded_filename)
                sanitized_name = sanitize_filename(base_name)
                sanitized_path = os.path.join(temp_dir, sanitized_name)
                os.rename(downloaded_filename, sanitized_path)

            # GCSにアップロード
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(sanitized_name)

            print(f"Uploading {sanitized_path} to gs://{BUCKET_NAME}/{sanitized_name}")
            blob.upload_from_filename(sanitized_path)
            print("Upload complete.")

            # 署名付きURLを生成 (有効期間1時間)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=60),
                method="GET",
            )

        return jsonify({
            'message': 'File successfully uploaded to GCS.',
            'download_url': signed_url,
            'gcs_path': f"gs://{BUCKET_NAME}/{sanitized_name}"
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
