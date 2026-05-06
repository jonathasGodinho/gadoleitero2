"""
Netlify Function wrapper for Terra Roxa Flask app
"""
import sys
import os
from io import BytesIO
from urllib.parse import urlencode

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import app, db, User, Animal, TipoRacao, PrecoLeite
from datetime import date
from werkzeug.security import generate_password_hash
import base64

# Initialize database on first run
_db_initialized = False

def init_db():
    global _db_initialized
    if not _db_initialized:
        db.create_all()
        if not Animal.query.first():
            db.session.add(Animal(nome='Bella', brinco='001', raca='Holandesa', lote='Lote A'))
            db.session.add(Animal(nome='Mimosa', brinco='002', raca='Girolanda', lote='Lote A'))
            db.session.add(Animal(nome='Estrela', brinco='003', raca='Jersey', lote='Lote B'))
        if not TipoRacao.query.first():
            db.session.add(TipoRacao(nome='Ração Padrão', preco_kg=3.50, tipo='concentrado'))
            db.session.add(TipoRacao(nome='Ração Premium', preco_kg=5.00, tipo='concentrado'))
        if not PrecoLeite.query.first():
            db.session.add(PrecoLeite(preco_litro=2.50, data_vigencia=date(2024, 1, 1)))
        if not User.query.filter_by(email='admin@terra-roxa.com').first():
            admin = User(
                email='admin@terra-roxa.com',
                nome='Administrador',
                senha_hash=generate_password_hash('admin123'),
                is_admin=True,
                role='admin'
            )
            db.session.add(admin)
        db.session.commit()
        _db_initialized = True

def handler(event, context):
    """Convert Netlify event to WSGI environ and call Flask app"""
    
    init_db()
    
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    headers = {k.lower(): v for k, v in event.get('headers', {}).items()}
    query_string = event.get('queryStringParameters', {}) or {}
    body = event.get('body', '') or ''
    is_base64 = event.get('isBase64Encoded', False)
    
    # Build request body
    if is_base64 and body:
        request_body = base64.b64decode(body)
    elif body:
        request_body = body.encode('utf-8')
    else:
        request_body = b''
    
    # Build query string
    qs = urlencode(query_string) if query_string else ''
    
    # Build WSGI environ
    server_name = headers.get('host', 'localhost').split(':')[0]
    
    environ = {
        'REQUEST_METHOD': http_method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': qs,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(request_body)),
        'SERVER_NAME': server_name,
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(request_body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers
    for key, value in headers.items():
        if key.lower() not in ('content-type', 'content-length', 'host'):
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Call WSGI app
    response_status = None
    response_headers = []
    response_body = []
    
    def start_response(status, headers, exc_info=None):
        nonlocal response_status
        response_status = status
        response_headers.extend(headers)
        return response_body.append
    
    result = app(environ, start_response)
    
    # Collect response
    body_chunks = []
    for chunk in result:
        body_chunks.append(chunk)
    if hasattr(result, 'close'):
        result.close()
    
    full_body = b''.join(body_chunks)
    
    # Build response headers dict
    resp_headers = {}
    for key, value in response_headers:
        resp_headers[key] = value
    
    # Parse status code
    status_code = int(response_status.split()[0])
    
    return {
        'statusCode': status_code,
        'headers': resp_headers,
        'body': full_body.decode('utf-8', errors='replace'),
        'isBase64Encoded': False
    }
