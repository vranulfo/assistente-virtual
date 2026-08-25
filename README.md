# Assistente de Letramento Digital

## Executar localmente

### 1. Banco de dados

Confirme que o serviço **MySQL94** está iniciado no Windows. Foi encontrado um dump em `C:\Users\User\Downloads\respostas.sql`, com seis registros antigos. O dump foi gerado pelo MariaDB e não contém a instrução `USE assistente`, então a restauração deve informar o banco pela linha de comando.

Crie o banco vazio somente se ele ainda não aparecer em `SHOW DATABASES`:

```sql
CREATE DATABASE assistente CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Antes de qualquer alteração estrutural, faça um backup do banco existente (se ele já tiver sido criado):

```powershell
& 'C:\Program Files\MySQL\MySQL Server 9.4\bin\mysqldump.exe' -u root -p assistente > backup-assistente.sql
```

Para restaurar o dump encontrado, execute no PowerShell:

```powershell
Get-Content 'C:\Users\User\Downloads\respostas.sql' -Raw | & 'C:\Program Files\MySQL\MySQL Server 9.4\bin\mysql.exe' -u root -p -D assistente
```

O dump antigo não possui a coluna `imagem`, mas o código atual suporta imagens. Depois da importação, adicione somente essa coluna:

```powershell
& 'C:\Program Files\MySQL\MySQL Server 9.4\bin\mysql.exe' -u root -p -D assistente -e "ALTER TABLE respostas ADD COLUMN imagem TEXT NULL;"
```

Para uma instalação nova sem dump, `schema.sql` usa `CREATE ... IF NOT EXISTS` e cria a estrutura completa.

O projeto espera a tabela `assistente.respostas` com as colunas `id`, `pergunta`, `resposta`, `proxima_pergunta` e `imagem`.

### 2. Configuração do backend

Na raiz do projeto:

```powershell
Copy-Item .env.example .env
```

Edite `.env` com o usuário e a senha reais do MySQL. O `.env` não deve ser enviado ao Git.

### 3. Ambiente Python

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 4. Backend

Em um terminal com o ambiente virtual ativo:

```powershell
Set-Location backend
python app.py
```

Teste em outro terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
Invoke-RestMethod http://127.0.0.1:5000/perguntas
```

O endpoint `/health` só retorna `ok` quando o Flask consegue acessar o MySQL.

### 5. Frontend

Em outro terminal:

```powershell
Set-Location frontend
python -m http.server 8000
```

Abra:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/admin.html`

O frontend usa `http://127.0.0.1:5000` por padrão. Para outro endereço, defina `window.APP_CONFIG.API_BASE_URL` antes de `frontend/js/config.js`.

## Dados existentes

Nenhum código deste projeto usa `respostas.json`; os dados vêm diretamente do MySQL. Não use `DROP DATABASE`, `DROP TABLE` ou `TRUNCATE` durante a preparação local.

## Publicar no GitHub e na Vercel

O projeto já inclui `vercel.json` e `api/index.py` para publicar o frontend e o Flask no mesmo projeto Vercel.

1. Crie o repositório local e publique a versão inicial:

```powershell
git init
git add .
git commit -m "Versao inicial"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

2. Crie uma branch para a apresentação e futuras alterações:

```powershell
git switch -c apresentacao
git push -u origin apresentacao
```

Assim, `main` fica como referência da versão inicial e as modificações podem ser feitas em `apresentacao`.

3. Na Vercel, importe o repositório do GitHub. Use a raiz do repositório como **Root Directory**, deixe o framework como **Other** e defina a branch de produção conforme a versão que deseja apresentar.

4. Cadastre na Vercel as variáveis `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME`. Elas devem apontar para um MySQL hospedado, como PlanetScale, Railway ou Aiven; o MySQL instalado no seu computador não pode ser acessado pela Vercel.

O endereço da API muda automaticamente: localmente continua em `127.0.0.1:5000` e, na Vercel, usa `/api` no mesmo domínio. Depois do deploy, teste `/api/health`.
