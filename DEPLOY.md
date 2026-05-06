# Guia de Deploy Gratuito - Terra Roxa System

## Opção Recomendada: Render.com (Grátis)

### Por que Render?
- ✅ PostgreSQL grátis (90 dias de retenção, renovável)
- ✅ Python support nativo
- ✅ HTTPS automático
- ✅ Deploy via GitHub

### Passo a Passo:

#### 1. Subir para o GitHub
```bash
git init
git add .
git commit -m "Sistema Terra Roxa pronto para produção"
git remote add origin https://github.com/seu-usuario/gadoleiteiro.git
git push -u origin main
```

#### 2. Criar Conta no Render
1. Acesse https://render.com
2. Clique em "Get Started for Free"
3. Faça login com GitHub

#### 3. Novo Web Service
1. No dashboard, clique em "New +" → "Web Service"
2. Conecte seu repositório `gadoleiteiro`
3. Configure:
   - **Name**: `terra-roxa-system`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn run:app`

#### 4. Configurar Banco de Dados (PostgreSQL Grátis)
1. No menu lateral, clique em "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `terra-roxa-db`
   - **Database**: `gadoleiteiro`
   - **User**: `admin`
   - **Plan**: **Free**
3. Clique em "Create Database"
4. Copie a **Internal Database URL** (será algo como `postgres://user:pass@host:5432/dbname`)

#### 5. Vincular Banco ao Web Service
1. Vá ao Web Service criado
2. Vá em "Environment" → "Add Environment Variable"
3. Adicione:
   - **Key**: `DATABASE_URL`
   - **Value**: (cole a URL do PostgreSQL copiada no passo 4)
4. Adicione também:
   - **Key**: `SECRET_KEY`
   - **Value**: (gere uma chave aleatória, ex: `openssl rand -hex 32`)

#### 6. Deploy Automático
- O Render fará o deploy automaticamente
- Aguarde ~5 minutos
- Acesse: `https://terra-roxa-system.onrender.com`

---

## Alternativas Gratuitas:

### Railway.app
- ✅ $5 de crédito grátis (suficiente para ~2 meses)
- ✅ PostgreSQL incluso
- 🔗 https://railway.app

### Fly.io
- ✅ Plano grátis limitado (3 pequenas VMs)
- ✅ PostgreSQL disponível
- 🔗 https://fly.io

---

## Configuração Pós-Deploy:

### 1. Criar Usuário Admin
Acesse o shell do Render ou use o endpoint de registro:
```
https://seu-app.onrender.com/register
```
Registre-se e depois altere no banco para `is_admin=True`.

### 2. Configurar Chave OpenWeatherMap (Opcional)
No Render Environment Variables, adicione:
- **Key**: `OPENWEATHER_API_KEY`
- **Value**: sua chave gratuita de https://openweathermap.org/api

---

## Observações Importantes:

⚠️ **Banco Grátis no Render**:
- Dados são mantidos por 90 dias (renováveis com login mensal)
- Para produção real, use plano pago ou outro provedor

⚠️ **Arquivos Estáticos**:
- Render serve arquivos estáticos automaticamente
- Para produção em escala, considere usar CDN (CloudFlare)

⚠️ **Sessões**:
- O SECRET_KEY deve ser alterado para produção
- Use cookies seguros em produção

---

## Testando Localmente com PostgreSQL:

```bash
# Instalar PostgreSQL localmente ou usar Docker
docker run -d --name terra-roxa-pg -e POSTGRES_PASSWORD=senha -e POSTGRES_DB=gadoleiteiro -p 5432:5432 postgres

# Configurar variável de ambiente
set DATABASE_URL=postgresql://postgres:senha@localhost:5432/gadoleiteiro

# Rodar migrações
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Rodar
python run.py
```

---

✅ **Pronto!** Seu sistema estará online gratuitamente em ~10 minutos.
