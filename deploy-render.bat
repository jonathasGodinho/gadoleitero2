@echo off
echo ==============================================
echo    TERRA ROXA - PREPARACAO PARA DEPLOY
echo ==============================================
echo.

echo [1/3] Verificando arquivos necessarios...
if not exist "requirements.txt" (
    echo ERRO: requirements.txt nao encontrado!
    pause
    exit /b 1
)
if not exist "Procfile" (
    echo ERRO: Procfile nao encontrado!
    pause
    exit /b 1
)
echo ✅ Arquivos OK!

echo.
echo [2/3] Gerando SECRET_KEY aleatoria...
powershell -Command "$key = -join ((1..64) | ForEach-Object { Get-Random -InputObject ([char[]]'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') }); Write-Output $key" > temp_key.txt
set /p SECRET_KEY=<temp_key.txt
del temp_key.txt
echo ✅ SECRET_KEY gerada: %SECRET_KEY:~0,20%...

echo.
echo [3/3] Instrucoes para Deploy no Render.com:
echo.
echo ==============================================
echo    PASSOS PARA DEPLOY GRATUITO
echo ==============================================
echo.
echo 1. Crie uma conta no GitHub (https://github.com)
echo 2. Crie um novo repositorio chamado "gadoleiteiro"
echo 3. Instale o Git: https://git-scm.com/download/win
echo 4. Apos instalar o Git, execute:
echo.
echo    git init
echo    git add .
echo    git commit -m "Sistema Terra Roxa pronto para producao"
echo    git remote add origin https://github.com/SEU-USUARIO/gadoleiteiro.git
echo    git push -u origin main
echo.
echo 5. Acesse https://render.com e faca login com GitHub
echo 6. Clique em "New +" → "Web Service"
echo 7. Conecte o repositorio "gadoleiteiro"
echo 8. Configure:
echo    - Name: terra-roxa-system
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: gunicorn run:app
echo.
echo 9. Clique em "Create Web Service"
echo.
echo 10. Va em "New +" → "PostgreSQL"
echo     - Name: terra-roxa-db
echo     - Plan: Free
echo     - Clique em "Create Database"
echo.
echo 11. Copie a "Internal Database URL" do banco criado
echo 12. No Web Service, va em "Environment"
echo     - Add Variable: DATABASE_URL = (cole a URL do PostgreSQL)
echo     - Add Variable: SECRET_KEY = %SECRET_KEY%
echo.
echo 13. Aguarde o deploy (5-10 minutos)
echo.
echo ✅ Seu sistema estara online em:
echo    https://terra-roxa-system.onrender.com
echo.
echo ==============================================
echo    CREDENCIAIS PADRAO
echo ==============================================
echo    Email: admin@terra-roxa.com
echo    Senha: admin123
echo.
echo IMPORTANTE: Altere a senha apos o primeiro login!
echo.
pause
