from flask import Blueprint, jsonify, request

from models.database import (
    _carregar_respostas,
    adicionar_resposta,
    buscar_pergunta,
    editar_resposta,
    listar_perguntas,
)

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/responder', methods=['POST'])
def responder():
    pergunta = (request.json or {}).get('pergunta', '').strip().lower()
    resultado = buscar_pergunta(pergunta)

    if not resultado:
        return jsonify({'resposta': 'Desculpe, não encontrei essa pergunta.', 'proximas': [], 'imagem_url': None})

    proximas_raw = resultado.get('proxima_pergunta') or ''
    proximas = [p.strip() for p in proximas_raw.split('|') if p.strip()]
    return jsonify({'resposta': resultado['resposta'], 'proximas': proximas, 'imagem_url': resultado.get('imagem')})


@chatbot_bp.route('/adicionar', methods=['POST'])
def adicionar():
    data = request.json or {}
    pergunta = data.get('pergunta', '').strip().lower()
    resposta = data.get('resposta', '').strip()
    proxima = data.get('proxima')
    imagem = data.get('imagem_url', data.get('imagem'))

    if not pergunta or not resposta:
        return jsonify({'mensagem': 'Preencha todos os campos.'}), 400

    adicionar_resposta(pergunta, resposta, proxima, imagem)
    return jsonify({'mensagem': 'Resposta adicionada com sucesso!'})


@chatbot_bp.route('/perguntas', methods=['GET'])
def perguntas():
    apenas_menu_principal = request.args.get('menu') == 'principal'
    return jsonify({
        'perguntas': listar_perguntas(
            apenas_menu_principal=apenas_menu_principal
        )
    })


@chatbot_bp.route('/editar/<int:id_resposta>', methods=['PUT'])
def editar(id_resposta):
    data = request.json or {}
    pergunta = data.get('pergunta', '').strip().lower()
    resposta = data.get('resposta', '').strip()
    proxima = data.get('proxima')
    imagem_url = data.get('imagem_url', data.get('imagem'))

    if not pergunta or not resposta:
        return jsonify({'mensagem': 'Preencha todos os campos.'}), 400

    editar_resposta(id_resposta, pergunta, resposta, proxima, imagem_url)
    return jsonify({'mensagem': 'Pergunta atualizada com sucesso!'})


@chatbot_bp.route('/perguntas_detalhadas', methods=['GET'])
def perguntas_detalhadas():
    resultados = _carregar_respostas()
    return jsonify({'perguntasDetalhadas': resultados})


@chatbot_bp.route('/health', methods=['GET'])
def health():
    try:
        _carregar_respostas()
        return jsonify({'status': 'ok', 'database': 'ok'})
    except Exception:
        return jsonify({'status': 'error', 'database': 'unavailable'}), 503
