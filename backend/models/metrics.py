import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from models.database import _conectar_postgres, usando_postgres


METRICS_FILE = Path(__file__).resolve().parent.parent / 'data' / 'metricas.json'
_metrics_lock = threading.Lock()


def _carregar_metricas():
    if not METRICS_FILE.exists() or not METRICS_FILE.read_text(encoding='utf-8').strip():
        return {}
    with METRICS_FILE.open(encoding='utf-8') as arquivo:
        return json.load(arquivo)


def registrar_tempo(tela, duracao_segundos):
    tela = tela.strip()[:255]
    duracao = float(duracao_segundos)
    if not tela or duracao < 1 or duracao > 1800:
        raise ValueError('Métrica inválida')

    if usando_postgres():
        with _conectar_postgres() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO metricas_tempo (tela, total_segundos, visualizacoes)
                    VALUES (%s, %s, 1)
                    ON CONFLICT (tela) DO UPDATE SET
                        total_segundos = metricas_tempo.total_segundos + EXCLUDED.total_segundos,
                        visualizacoes = metricas_tempo.visualizacoes + 1,
                        ultima_atualizacao = CURRENT_TIMESTAMP
                ''', (tela, duracao))
        return

    with _metrics_lock:
        metricas = _carregar_metricas()
        atual = metricas.setdefault(tela, {'total_segundos': 0, 'visualizacoes': 0})
        atual['total_segundos'] = round(float(atual['total_segundos']) + duracao, 2)
        atual['visualizacoes'] = int(atual['visualizacoes']) + 1
        atual['ultima_atualizacao'] = datetime.now(timezone.utc).isoformat()
        METRICS_FILE.write_text(
            json.dumps(metricas, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )


def resumir_tempos():
    if usando_postgres():
        with _conectar_postgres() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute('''
                    SELECT tela, visualizacoes, total_segundos,
                           CASE WHEN visualizacoes > 0
                                THEN total_segundos / visualizacoes ELSE 0 END
                    FROM metricas_tempo
                    ORDER BY 4 DESC
                ''')
                return [
                    {
                        'tela': linha[0],
                        'visualizacoes': linha[1],
                        'tempo_total_segundos': round(float(linha[2]), 2),
                        'tempo_medio_segundos': round(float(linha[3]), 2),
                    }
                    for linha in cursor.fetchall()
                ]

    metricas = _carregar_metricas()
    resultados = []
    for tela, valores in metricas.items():
        visualizacoes = int(valores.get('visualizacoes', 0))
        total = float(valores.get('total_segundos', 0))
        resultados.append({
            'tela': tela,
            'visualizacoes': visualizacoes,
            'tempo_total_segundos': round(total, 2),
            'tempo_medio_segundos': round(total / visualizacoes, 2) if visualizacoes else 0,
        })
    return sorted(resultados, key=lambda item: item['tempo_medio_segundos'], reverse=True)
