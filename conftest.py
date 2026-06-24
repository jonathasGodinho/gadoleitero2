import pytest
from flask import Flask
from flask_login import LoginManager
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from extensions import db as _db, login_manager, csrf, limiter
from models import User, Animal, TipoRacao, PrecoLeite, ProducaoLeite, ConsumoRacao, Despesa, Cliente, VendaAvulsa, SaudeAnimal, Orcamento


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.secret_key = 'test-secret-key'

    _db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    limiter.init_app(app)
    limiter.enabled = False

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_globals():
        return dict(
            preco_vigente_global=2.20, data_cotacao_global='01/01/2024',
            qtd_alertas_saude=0, date=date,
            csrf_token_input='<input type="hidden" name="csrf_token" value="test">',
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

    with app.app_context():
        _db.create_all()
        _seed_data()

    yield app

    with app.app_context():
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def login_admin(client):
    client.post('/login', data={'email': 'admin@teste.com', 'password': 'admin123'})


@pytest.fixture
def login_operador(client):
    client.post('/login', data={'email': 'operador@teste.com', 'password': 'oper123'})


def _seed_data():
    admin = User(
        email='admin@teste.com', nome='Admin Teste',
        senha_hash=generate_password_hash('admin123'),
        is_admin=True, role='admin', ativo=True,
    )
    operador = User(
        email='operador@teste.com', nome='Operador Teste',
        senha_hash=generate_password_hash('oper123'),
        is_admin=False, role='operador', ativo=True,
    )
    _db.session.add_all([admin, operador])

    animais = [
        Animal(nome='Bella', brinco='T001', raca='Holandesa', sexo='femea', lote='Lote A', ativo=True),
        Animal(nome='Mimosa', brinco='T002', raca='Girolanda', sexo='femea', lote='Lote A', ativo=True),
    ]
    _db.session.add_all(animais)
    _db.session.flush()

    racoes = [
        TipoRacao(nome='Racao Teste A', preco_kg=3.50, tipo='concentrado'),
        TipoRacao(nome='Racao Teste B', preco_kg=5.00, tipo='concentrado'),
    ]
    _db.session.add_all(racoes)
    _db.session.flush()

    _db.session.add(PrecoLeite(preco_litro=2.20, data_vigencia=date(2024, 1, 1)))

    hoje = date.today()
    for i in range(3):
        d = hoje - timedelta(days=i)
        prod = ProducaoLeite(litros=25.0 + i, data=d, preco_venda=2.20, total_receber=(25.0 + i) * 2.20)
        _db.session.add(prod)

        _db.session.add(ConsumoRacao(
            animal_id=animais[0].id, tipo_racao_id=racoes[0].id,
            quantidade_kg=10.0, data=d, custo=35.0,
        ))

        _db.session.add(Despesa(
            descricao=f'Despesa {i}', valor=100.0 + i,
            categoria='manutencao', data=d,
        ))

    clientes = [
        Cliente(nome='Cliente Teste A', telefone='11999990001', email='cliente@teste.com'),
        Cliente(nome='Cliente Teste B', telefone='11999990002'),
    ]
    _db.session.add_all(clientes)
    _db.session.flush()

    _db.session.add(VendaAvulsa(
        cliente_id=clientes[0].id, data=hoje,
        litros=50.0, valor_litro=3.00, total=150.0,
    ))

    _db.session.add(SaudeAnimal(
        animal_id=animais[0].id, tipo='vermifugo',
        data_aplicacao=hoje - timedelta(days=30), proxima_dose=hoje + timedelta(days=30),
        custo=50.0,
    ))

    _db.session.add(Orcamento(ano=hoje.year, mes=hoje.month, categoria='racao', valor_previsto=2000.0))

    _db.session.commit()
