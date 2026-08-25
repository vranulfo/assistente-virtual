import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_resposta(pergunta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT resposta FROM respostas WHERE pergunta = %s", (pergunta,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Desculpe, não entendi. Tente outra pergunta."

def adicionar_resposta(pergunta, resposta, proxima=None, imagem_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO respostas (pergunta, resposta, proxima_pergunta, imagem) VALUES (%s, %s, %s, %s)",
        (pergunta, resposta, proxima, imagem_url)
    )
    conn.commit()
    conn.close()

def listar_perguntas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pergunta FROM respostas")
    perguntas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return perguntas

def buscar_pergunta(pergunta):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT pergunta, resposta, proxima_pergunta, imagem FROM respostas WHERE LOWER(pergunta) = LOWER(%s)", (pergunta,))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado

def editar_resposta(id_resposta, nova_pergunta, nova_resposta, nova_proxima=None, nova_imagem_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE respostas
        SET pergunta = %s,
            resposta = %s,
            proxima_pergunta = %s,
            imagem = %s
        WHERE id = %s
    """, (nova_pergunta, nova_resposta, nova_proxima, nova_imagem_url, id_resposta))
    conn.commit()
    conn.close()
