import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / 'data' / 'respostas.json'


def _carregar_respostas():
    if not DATA_FILE.exists() or not DATA_FILE.read_text(encoding='utf-8').strip():
        return []

    with DATA_FILE.open(encoding='utf-8') as arquivo:
        return json.load(arquivo)


def _salvar_respostas(respostas):
    DATA_FILE.write_text(
        json.dumps(respostas, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )


def listar_perguntas():
    return [item['pergunta'] for item in _carregar_respostas()]


def buscar_pergunta(pergunta):
    pergunta_normalizada = pergunta.strip().lower()
    return next(
        (
            item for item in _carregar_respostas()
            if item.get('pergunta', '').lower() == pergunta_normalizada
        ),
        None,
    )


def adicionar_resposta(pergunta, resposta, proxima=None, imagem_url=None):
    respostas = _carregar_respostas()
    proximo_id = max((item.get('id', 0) for item in respostas), default=0) + 1
    respostas.append({
        'id': proximo_id,
        'pergunta': pergunta,
        'resposta': resposta,
        'proxima_pergunta': proxima or '',
        'imagem': imagem_url or None,
    })
    _salvar_respostas(respostas)


def editar_resposta(id_resposta, nova_pergunta, nova_resposta, nova_proxima=None, nova_imagem_url=None):
    respostas = _carregar_respostas()
    for item in respostas:
        if item.get('id') == id_resposta:
            item.update({
                'pergunta': nova_pergunta,
                'resposta': nova_resposta,
                'proxima_pergunta': nova_proxima or '',
                'imagem': nova_imagem_url or None,
            })
            _salvar_respostas(respostas)
            return True
    return False
