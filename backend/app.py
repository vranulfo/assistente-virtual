import os
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory, session, url_for
from flask_cors import CORS
from auth import admin_autenticado, senha_admin_configurada, senha_admin_valida
from routes.chatbot import chatbot_bp

FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY') or os.urandom(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('VERCEL_ENV') in {'production', 'preview'},
)
CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(chatbot_bp)


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/admin.html')
def admin():
    if not admin_autenticado():
        return redirect(url_for('login'))
    return send_from_directory(FRONTEND_DIR, 'admin.html')


@app.route('/login.html')
def login():
    if admin_autenticado():
        return redirect(url_for('admin'))
    return send_from_directory(FRONTEND_DIR, 'login.html')


@app.route('/admin/login', methods=['POST'])
def realizar_login():
    if not senha_admin_configurada():
        return jsonify({'mensagem': 'ADMIN_PASSWORD não foi configurada no servidor.'}), 503
    senha = (request.json or {}).get('senha', '')
    if not senha_admin_valida(senha):
        return jsonify({'mensagem': 'Senha incorreta.'}), 401
    session.clear()
    session['admin_autenticado'] = True
    return jsonify({'mensagem': 'Login realizado.'})


@app.route('/admin/logout', methods=['POST'])
def realizar_logout():
    session.clear()
    return jsonify({'mensagem': 'Sessão encerrada.'})


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
