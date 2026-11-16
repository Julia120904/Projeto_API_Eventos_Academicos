# API de Gestão de Eventos Acadêmicos — Segunda Unidade

API desenvolvida com FastAPI para gerenciamento de usuários, categorias, eventos, inscrições e certificados. Esta versão mantém os CRUDs da Primeira Unidade e adiciona autenticação e autorização com JWT.

## Tecnologias

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite (configuração local padrão) ou PostgreSQL
- Argon2id (`argon2-cffi`) para hash de senhas
- JWT HS256 com expiração
- Alembic para migrações

## 1. Preparar o ambiente

No terminal, dentro da pasta `Projeto_API_Eventos_Academicos`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copie o arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

Abra o `.env` e substitua `JWT_SECRET_KEY` por uma chave aleatória. Para gerar uma:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Cole o resultado em `JWT_SECRET_KEY`. Altere também `ADMIN_PASSWORD` para uma senha forte. Não publique o `.env` no GitHub.

## 2. Atualizar o banco de dados

### Se estiver usando o banco SQLite que já veio com o projeto

O banco da Primeira Unidade já possui as tabelas, mas ainda não tem a tabela de controle do Alembic. Execute uma única vez:

```powershell
alembic stamp 0001_initial
alembic upgrade head
```

A migração adiciona `password_hash` à tabela de usuários e preserva os registros existentes. Os usuários antigos ficam sem senha até que um administrador defina uma senha para eles.

### Se estiver usando um banco vazio

```powershell
alembic upgrade head
```

Se preferir PostgreSQL, configure `DATABASE_URL` no `.env` com a URL do PostgreSQL e execute as migrações nesse banco.

## 3. Criar o administrador inicial

Depois de configurar o `.env` e atualizar o banco:

```powershell
python -m app.seed_admin
```

O script cria (ou atualiza) a conta de administrador definida por `ADMIN_EMAIL` e `ADMIN_PASSWORD`. Esse provisionamento inicial é necessário para administrar usuários e categorias.

## 4. Executar a API

```powershell
uvicorn app.main:app --reload
```

Abra o Swagger:

- http://127.0.0.1:8000/docs

## 5. Fluxo de autenticação no Swagger

1. Abra `POST /api/v1/auth/login`.
2. Informe `email` e `password` da conta administradora criada no passo anterior.
3. Copie o valor de `access_token` retornado.
4. Clique em **Authorize** no topo do Swagger.
5. Cole o token no campo Bearer e confirme.
6. Execute uma rota protegida, como `GET /api/v1/usuarios/me` ou `POST /api/v1/categorias`.
7. Para testar o bloqueio, clique em **Authorize > Logout** e execute novamente uma rota protegida. O resultado esperado é `401 Unauthorized`.

## 6. Endpoints principais

### Autenticação

| Método | Rota | Acesso |
|---|---|---|
| POST | `/api/v1/auth/registrar` | Público — cria participante |
| POST | `/api/v1/auth/login` | Público — retorna JWT |
| GET | `/api/v1/auth/me` | Autenticado |
| GET | `/api/v1/usuarios/me` | Autenticado |

### Usuários

| Método | Rota | Acesso |
|---|---|---|
| POST | `/api/v1/usuarios` | Administrador |
| GET | `/api/v1/usuarios` | Administrador |
| GET | `/api/v1/usuarios/{id}` | Administrador |
| PUT | `/api/v1/usuarios/{id}` | Administrador |
| DELETE | `/api/v1/usuarios/{id}` | Administrador |

O cadastro público em `/auth/registrar` cria somente usuários com perfil `participante`. O administrador pode provisionar usuários com outros perfis e senha pelo CRUD de usuários.

### Rotas protegidas por perfil

- Criar/alterar/excluir categorias: administrador.
- Criar eventos: organizador ou administrador.
- Alterar/excluir eventos: administrador ou organizador responsável pelo evento.
- Criar/cancelar inscrição: participante autenticado (somente a própria inscrição) ou administrador.
- Emitir certificados: organizador ou administrador.

As consultas públicas de eventos e categorias foram mantidas para preservar a descoberta de eventos. Consultas de usuários, inscrições e certificados exigem autenticação e respeitam o perfil do usuário. Rotas que alteram dados sensíveis também exigem autenticação e, quando aplicável, perfil autorizado.

## 7. Códigos de resposta de segurança

- `200/201`: operação realizada.
- `401 Unauthorized`: token ausente, inválido ou expirado; ou credenciais de login incorretas.
- `403 Forbidden`: usuário autenticado, mas sem perfil/permissão para a operação.
- `422 Unprocessable Entity`: dados enviados fora do formato esperado.

## 8. Evidências para a entrega

1. Código atualizado e enviado ao GitHub.
2. Swagger exibindo as tags **Autenticação**, **Usuários** e os demais CRUDs.
3. `POST /auth/login` retornando `access_token`.
4. Botão **Authorize** com token válido.
5. `GET /usuarios/me` retornando os dados do usuário autenticado.
6. Rota protegida funcionando com token válido.
7. Mesma rota retornando `401` sem token ou com token inválido.

## Observações

- Senhas nunca são retornadas pela API; somente o hash Argon2 fica armazenado.
- O token JWT expira após o período configurado em `ACCESS_TOKEN_EXPIRE_MINUTES` (padrão: 30 minutos).
- A chave JWT deve ficar somente no `.env`, que está listado no `.gitignore`.
- Usuários que já existiam no banco antes desta atualização não possuem senha automaticamente. Defina uma senha para eles pelo CRUD administrativo (`PUT /api/v1/usuarios/{id}`) ou cadastre uma nova conta de participante.
