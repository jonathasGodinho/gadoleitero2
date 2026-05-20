from app import app, db
from init_db import init_database

# Inicializa banco de dados na inicialização (funciona com gunicorn)
init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f'Servidor iniciando na porta {port}...')
    app.run(host='0.0.0.0', port=port, debug=debug)
