# Assistente de Letramento Digital

Aplicacao web acessivel para consultar respostas de letramento digital. A versao da Vercel usa um arquivo JSON, sem banco externo.

## Estrutura

- `frontend/`: paginas, estilos e scripts
- `backend/`: API Flask
- `backend/data/respostas.json`: perguntas e respostas publicadas
- `api/index.py`: entrada da API na Vercel

## Publicar na Vercel

1. Na Vercel, importe o repositorio `vranulfo/assistente-virtual`.
2. Mantenha **Root Directory** como `./` e o preset **Flask**.
3. Nao preencha variaveis `DB_*`; esta versao nao usa MySQL.
4. Clique em **Deploy**.

A Vercel hospeda o frontend e executa a API automaticamente. Nao e necessario manter terminal, Flask ou `.venv` abertos.

## Adicionar ou alterar respostas

O painel `/admin.html` permite testar o cadastro localmente, mas a Vercel nao grava alteracoes no arquivo JSON de forma permanente. Para publicar uma nova resposta:

1. Abra `backend/data/respostas.json`.
2. Adicione um objeto neste formato:

```json
{
  "id": 7,
  "pergunta": "como criar uma senha segura?",
  "resposta": "Use uma senha longa, unica e dificil de adivinhar.",
  "proxima_pergunta": "como proteger minha conta?",
  "imagem": null
}
```

3. Use um `id` diferente em cada objeto. Se houver varias perguntas, mantenha todos dentro de uma lista entre `[` e `]`, separados por virgula.
4. Teste localmente e publique:

```powershell
.\.venv\Scripts\Activate.ps1
python backend/app.py
```

Em outro terminal, abra o frontend local ou use o deploy atual para consultar. Depois:

```powershell
git switch alteracao-vercel
git add backend/data/respostas.json
git commit -m "Atualiza respostas"
git push origin alteracao-vercel
```

A Vercel criara um deployment de preview para a branch. Para atualizar a apresentacao principal, faca merge da branch para `main` no GitHub ou selecione `alteracao-vercel` como **Production Branch** na Vercel.

## Desenvolvimento local

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python backend/app.py
```

O backend fica em `http://127.0.0.1:5000`. O frontend pode ser servido com `python -m http.server 8000` dentro de `frontend`.
