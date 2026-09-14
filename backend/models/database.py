import json
import os
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / 'data' / 'respostas.json'


def _database_url():
    return os.getenv('DATABASE_URL', '').strip()


def usando_postgres():
    return bool(_database_url())


def _conectar_postgres():
    import psycopg
    return psycopg.connect(_database_url())


def _carregar_respostas():
    if usando_postgres():
        with _conectar_postgres() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute('''
                    SELECT id, pergunta, resposta, proxima_pergunta, imagem,
                           menu_principal, categoria, descricao, icone
                    FROM respostas
                    ORDER BY id
                ''')
                colunas = [coluna.name for coluna in cursor.description]
                return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

    if not DATA_FILE.exists() or not DATA_FILE.read_text(encoding='utf-8').strip():
        return []

    with DATA_FILE.open(encoding='utf-8') as arquivo:
        return json.load(arquivo)


def _salvar_respostas(respostas):
    DATA_FILE.write_text(
        json.dumps(respostas, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )


def listar_perguntas(apenas_menu_principal=False):
    respostas = _carregar_respostas()
    if apenas_menu_principal:
        respostas = [
            item for item in respostas
            if item.get('menu_principal', False)
        ]
    return [item['pergunta'] for item in respostas]


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
    if usando_postgres():
        with _conectar_postgres() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO respostas (pergunta, resposta, proxima_pergunta, imagem)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                ''', (pergunta, resposta, proxima or '', imagem_url or None))
                return cursor.fetchone()[0]

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
    if usando_postgres():
        with _conectar_postgres() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute('''
                    UPDATE respostas
                    SET pergunta = %s, resposta = %s, proxima_pergunta = %s, imagem = %s
                    WHERE id = %s
                ''', (
                    nova_pergunta, nova_resposta, nova_proxima or '',
                    nova_imagem_url or None, id_resposta,
                ))
                return cursor.rowcount > 0

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
