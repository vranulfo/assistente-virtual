CREATE DATABASE IF NOT EXISTS assistente
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE assistente;

CREATE TABLE IF NOT EXISTS respostas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pergunta VARCHAR(255) NOT NULL,
    resposta TEXT NOT NULL,
    proxima_pergunta TEXT NULL,
    imagem TEXT NULL
);
