from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.chatbot import chatbot_bp

FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(chatbot_bp)


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/admin.html')
def admin():
    return send_from_directory(FRONTEND_DIR, 'admin.html')


@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(FRONTEND_DIR / 'css', filename)


@app.route('/js/<path:filename>')
def javascript(filename):
    return send_from_directory(FRONTEND_DIR / 'js', filename)


@app.route('/img/<path:filename>')
def image(filename):
    return send_from_directory(FRONTEND_DIR / 'img', filename)

if __name__ == '__main__':
    app.run(debug=False)
