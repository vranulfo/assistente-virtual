# Assistente de Letramento Digital

Aplicacao web acessivel para consultar respostas de letramento digital. O projeto usa o arquivo JSON localmente e passa a usar PostgreSQL quando a variavel `DATABASE_URL` esta configurada.

## Estrutura

- `frontend/`: paginas, estilos e scripts
- `backend/`: API Flask
- `backend/data/respostas.json`: perguntas e respostas publicadas
- `api/index.py`: entrada da API na Vercel

## Publicar na Vercel

1. Na Vercel, importe o repositorio `vranulfo/assistente-virtual`.
2. Mantenha **Root Directory** como `./` e o preset **Flask**.
3. Para usar dados persistentes, conecte um banco Neon e confirme que a variavel `DATABASE_URL` foi criada.
4. Clique em **Deploy**.

A Vercel hospeda o frontend e executa a API automaticamente. Nao e necessario manter terminal, Flask ou `.venv` abertos.

## Banco persistente com Neon

1. No painel da Vercel, abra o projeto e entre em **Storage**.
2. Selecione **Create Database**, escolha **Neon** e o plano gratuito.
3. Conecte o banco aos ambientes **Production**, **Preview** e **Development**. Prefira uma regiao proxima da regiao das funcoes da Vercel.
4. Confirme em **Settings > Environment Variables** que `DATABASE_URL` existe. Nunca copie essa URL para o Git.
5. Instale as dependencias atualizadas localmente:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

6. Copie temporariamente a URL de conexao do painel Neon para a sessao atual do PowerShell e execute a migracao:

```powershell
$env:DATABASE_URL = "postgresql://..."
python scripts/migrar_json_postgres.py
```

A migracao cria as tabelas, copia as respostas em uma unica transacao e valida os registros. Em caso de erro, a transacao e revertida. O arquivo `backend/data/respostas.json` nunca e apagado e continua sendo o backup/fallback local.

Para testar o banco antes de publicar:

```powershell
python backend/app.py
```

Abra `http://127.0.0.1:5000/health`. O campo `armazenamento` deve mostrar `postgres`. Depois teste o assistente e `/admin.html`. Somente apos essas verificacoes, envie o codigo ao GitHub e faça um novo deploy na Vercel.

## Proteger o painel administrativo

O acesso a `/admin.html`, as alteracoes de respostas e a consulta das metricas exigem uma sessao administrativa. Configure estas variaveis em **Vercel > Settings > Environment Variables** para Production, Preview e Development:

- `ADMIN_PASSWORD`: uma senha forte e exclusiva para entrar no painel.
- `SECRET_KEY`: uma chave aleatoria usada para assinar o cookie da sessao.

Gere a `SECRET_KEY` localmente com:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para a variavel na Vercel, sem salvar no repositorio. Para testar localmente, defina as duas variaveis apenas na sessao atual do PowerShell:

```powershell
$env:ADMIN_PASSWORD = "sua-senha-forte"
$env:SECRET_KEY = "a-chave-aleatoria-gerada"
```

O assistente publico e o registro anonimo de tempo continuam acessiveis sem login. Use `/login.html` para entrar no painel e o botao **Sair** para encerrar a sessao.

## Adicionar ou alterar respostas

Com `DATABASE_URL` configurada, as inclusoes e edicoes feitas em `/admin.html` sao persistidas no PostgreSQL. Sem essa variavel, o painel altera apenas o arquivo JSON local; a Vercel nao preserva essas gravacoes em arquivo.

O JSON continua sendo uma forma segura de preparar ou recuperar o conteudo. Para publicar uma resposta por arquivo:

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

## Métricas de tempo por tela

O assistente registra anonimamente quanto tempo a aba permaneceu visível no menu principal e em cada resposta. Visitas menores que 1 segundo ou maiores que 30 minutos são descartadas. As médias, quantidades de visualizações e tempos totais aparecem em `/admin.html`.

Sem `DATABASE_URL`, os dados ficam em `backend/data/metricas.json`. Com o Neon configurado, as metricas ficam persistentemente na tabela `metricas_tempo` e podem ser consultadas em `/admin.html`.

## Testes automáticos

Com o ambiente virtual ativo e as dependências instaladas, execute:

```powershell
python -m unittest discover -s tests -v
```

Os testes verificam a estrutura do JSON, IDs duplicados, encadeamento dos fluxos, imagens locais e os principais endpoints da API.
