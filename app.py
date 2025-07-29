from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    # ルートURLにアクセスがあったら、このメッセージを返す
    return "Hello from Cloud Run! The application is running correctly."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
