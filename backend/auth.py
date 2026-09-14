import hmac
import os
from functools import wraps

from flask import jsonify, session


def senha_admin_configurada():
    tem_senha = bool(os.getenv('ADMIN_PASSWORD', '').strip())
    tem_chave_estavel = bool(os.getenv('SECRET_KEY', '').strip()) or not os.getenv('VERCEL_ENV')
    return tem_senha and tem_chave_estavel


def senha_admin_valida(senha):
    esperada = os.getenv('ADMIN_PASSWORD', '')
    return bool(esperada) and hmac.compare_digest(str(senha), esperada)


def admin_autenticado():
    return session.get('admin_autenticado') is True


def admin_required(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if not admin_autenticado():
            return jsonify({'mensagem': 'Autenticação necessária.'}), 401
        return funcao(*args, **kwargs)
    return protegida
