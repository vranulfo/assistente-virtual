import json
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT_DIR / 'backend' / 'data' / 'respostas.json'
SCHEMA_FILE = ROOT_DIR / 'schema.sql'


def migrar():
    database_url = os.getenv('DATABASE_URL', '').strip()
    if not database_url:
        raise RuntimeError('Defina DATABASE_URL antes de executar a migração.')

    import psycopg

    respostas = json.loads(DATA_FILE.read_text(encoding='utf-8'))
    if not respostas:
        raise RuntimeError('O JSON não contém respostas para migrar.')

    with psycopg.connect(database_url) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(SCHEMA_FILE.read_text(encoding='utf-8'))
            for item in respostas:
                cursor.execute('''
                    INSERT INTO respostas (
                        id, pergunta, resposta, proxima_pergunta, imagem,
                        menu_principal, categoria, descricao, icone
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        pergunta = EXCLUDED.pergunta,
                        resposta = EXCLUDED.resposta,
                        proxima_pergunta = EXCLUDED.proxima_pergunta,
                        imagem = EXCLUDED.imagem,
                        menu_principal = EXCLUDED.menu_principal,
                        categoria = EXCLUDED.categoria,
                        descricao = EXCLUDED.descricao,
                        icone = EXCLUDED.icone
                ''', (
                    item['id'], item['pergunta'], item['resposta'],
                    item.get('proxima_pergunta', ''), item.get('imagem'),
                    item.get('menu_principal', False), item.get('categoria'),
                    item.get('descricao'), item.get('icone'),
                ))

            ids = [item['id'] for item in respostas]
            cursor.execute(
                'SELECT id, pergunta, resposta FROM respostas WHERE id = ANY(%s)',
                (ids,),
            )
            importadas = {linha[0]: linha[1:] for linha in cursor.fetchall()}
            for item in respostas:
                if importadas.get(item['id']) != (item['pergunta'], item['resposta']):
                    raise RuntimeError(f"Falha ao validar a resposta id={item['id']}.")

            cursor.execute('''
                SELECT setval(
                    pg_get_serial_sequence('respostas', 'id'),
                    (SELECT MAX(id) FROM respostas)
                )
            ''')

    print(f'Migração concluída e validada: {len(respostas)} respostas copiadas.')
    print(f'O arquivo original continua preservado em: {DATA_FILE}')


if __name__ == '__main__':
    try:
        migrar()
    except Exception as erro:
        print(f'Migração cancelada: {erro}', file=sys.stderr)
        print('Nenhuma alteração parcial foi confirmada no banco.', file=sys.stderr)
        raise SystemExit(1)
