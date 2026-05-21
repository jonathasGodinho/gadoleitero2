import sys
from app import app, db
from init_db import init_database

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
