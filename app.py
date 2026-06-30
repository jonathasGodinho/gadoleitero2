"""
Terra Roxa System - Sistema Completo de Gestão de Fazenda Leiteira
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import generate_csrf
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import date, timedelta
import os
import secrets

from extensions import db, migrate, login_manager, csrf, limiter
from models import User, SaudeAnimal
from utils import get_preco_vigente

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gadoleiteiro.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['JSON_AS_ASCII'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_cotacao():
        hoje = date.today()
        preco = get_preco_vigente(hoje)
        data_fmt = hoje.strftime('%d/%m/%Y')
        alertas = SaudeAnimal.query.filter(
            SaudeAnimal.proxima_dose <= hoje + timedelta(days=7),
            SaudeAnimal.proxima_dose >= hoje
        ).count()
        csrf_input = f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">'
        return dict(
            preco_vigente_global=preco, data_cotacao_global=data_fmt,
            qtd_alertas_saude=alertas, date=date,
            csrf_token_input=csrf_input
        )

    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.geral import geral_bp
    from routes.producao import producao_bp
    from routes.animais import animais_bp
    from routes.racao import racao_bp
    from routes.financeiro import financeiro_bp
    from routes.relatorios import relatorios_bp
    from routes.vendas import vendas_bp
    from routes.admin import admin_bp
    from routes.dieta import dieta_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(geral_bp)
    app.register_blueprint(producao_bp)
    app.register_blueprint(animais_bp)
    app.register_blueprint(racao_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(vendas_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dieta_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
