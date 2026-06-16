import sys
from app import app, db
from init_db import init_database
from backup_util import auto_backup, should_daily_backup

print('[run] Verificando backup automatico...')
try:
    if should_daily_backup():
        path = auto_backup(app, db)
        if path:
            print(f'[run] Backup diario salvo em: {path}')
        else:
            print('[run] Nenhum dado para backup (banco vazio)')
    else:
        print('[run] Backup diario ja realizado hoje')
except Exception as e:
    print(f'[run] Erro no backup automatico: {e}', file=sys.stderr)

try:
    init_database()
except Exception as e:
    print(f'[run] Erro na inicializacao do banco: {e}', file=sys.stderr)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f'Servidor iniciando na porta {port}...')
    app.run(host='0.0.0.0', port=port, debug=debug)
