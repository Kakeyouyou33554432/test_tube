import os
import logging
import tempfile
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from google.cloud import storage
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
logging.info("--- Application starting up ---")
app = Flask(__name__)
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
if not BUCKET_NAME:
    logging.error("FATAL: GCS_BUCKET_NAME environment variable is not set.")
logging.info(f"GCS_BUCKET_NAME is set to: {BUCKET_NAME}")

def sanitize_filename(filename, max_length=100):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '#']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:max_length]

@app.route('/')
def index():
    return "YouTube Downloader API is running.", 200

@app.route('/download', methods=['POST'])
def download_video():
    logging.info("Received request for /download endpoint.")
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL not provided'}), 400
    video_url = data['url']
    try:
        logging.info(f"Fetching video info for {video_url}")
        with YoutubeDL({'noplaylist': True, 'quiet': True}) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            title = info_dict.get('title', 'video')
            sanitized_title = sanitize_filename(title)
            final_filename = f"{sanitized_title}.mp4"
        logging.info(f"Final filename will be: {final_filename}")
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, final_filename),
                'merge_output_format': 'mp4',
                'noplaylist': True,
            }
            logging.info(f"Starting download to {temp_dir}")
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            logging.info("Download finished.")
            local_filepath = os.path.join(temp_dir, final_filename)
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(final_filename)
            logging.info(f"Uploading {local_filepath} to gs://{BUCKET_NAME}/{final_filename}")
            blob.upload_from_filename(local_filepath)
            logging.info("Upload to GCS complete.")
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=60),
                method="GET",
            )
        return jsonify({
            'message': 'File successfully uploaded to GCS.',
            'download_url': signed_url,
            'gcs_path': f"gs://{BUCKET_NAME}/{final_filename}"
        })
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
