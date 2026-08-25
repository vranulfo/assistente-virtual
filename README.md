# Assistente de Letramento Digital

Aplicacao web com frontend acessivel e API Flask para consultar e cadastrar respostas de letramento digital.

## Estrutura

- `frontend/`: paginas HTML, estilos e JavaScript
- `backend/`: aplicacao Flask e acesso ao MySQL
- `api/index.py`: entrada da API para a Vercel
- `schema.sql`: estrutura inicial do banco de dados

## Executar localmente

1. Crie um banco MySQL e execute o conteudo de `schema.sql`.
2. Copie `.env.example` para `.env` e preencha as credenciais do banco:

```powershell
Copy-Item .env.example .env
```

3. Instale as dependencias e inicie o backend:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Set-Location backend
python app.py
```

4. Em outro terminal, sirva o frontend:

```powershell
Set-Location frontend
python -m http.server 8000
```

Abra `http://127.0.0.1:8000/` ou `http://127.0.0.1:8000/admin.html`.

<<<<<<< HEAD
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/admin.html`
=======
## Publicar na Vercel
>>>>>>> 3297f25 (Limpa documentacao para publicacao)

O projeto possui `vercel.json` e funciona sem manter um servidor local ligado. A Vercel executa a API sob demanda e publica o frontend no mesmo dominio.

1. Na Vercel, selecione **Add New Project** e importe este repositorio do GitHub.
2. Use a raiz do repositorio como **Root Directory** e selecione **Other** como framework.
3. Em **Settings > Environment Variables**, cadastre `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME`.
4. Use um MySQL hospedado e acessivel pela internet. Um banco instalado apenas no seu computador nao funciona na Vercel.
5. Faca o primeiro deploy e teste `https://SEU_PROJETO.vercel.app/api/health`.

Depois da configuracao, cada push na branch de producao gera um novo deploy automaticamente. Pushes em outras branches criam deployments de preview, uteis para testar mudancas sem alterar a apresentacao principal.

## Fluxo de branches

`main` contem a versao inicial publicada. A branch `apresentacao` e usada para alteracoes:

```powershell
git switch apresentacao
git add .
git commit -m "Atualiza projeto"
git push origin apresentacao
```

Na Vercel, escolha `main` como **Production Branch** para manter a versao inicial como apresentacao. Para apresentar alteracoes, altere essa opcao para `apresentacao` ou use o link do deployment de preview.

Nunca publique o arquivo `.env`. Use as variaveis de ambiente da Vercel para as credenciais do banco.
