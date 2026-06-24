from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    nome = db.Column(db.String(150))
    senha_hash = db.Column(db.String(500))
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='operador')
    ativo = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    acao = db.Column(db.String(200))
    detalhes = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.relationship('User', backref='logs')

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    brinco = db.Column(db.String(50), unique=True, nullable=False)
    raca = db.Column(db.String(100))
    sexo = db.Column(db.String(10))
    lote = db.Column(db.String(50))
    ativo = db.Column(db.Boolean, default=True)
    data_ultima_inseminacao = db.Column(db.Date)
    data_parto_prevista = db.Column(db.Date)
    status_reproducao = db.Column(db.String(50), default='vazio')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SaudeAnimal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False, index=True)
    tipo = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    data_aplicacao = db.Column(db.Date, nullable=False)
    proxima_dose = db.Column(db.Date, index=True)
    custo = db.Column(db.Numeric(10, 2))
    observacoes = db.Column(db.Text)
    animal = db.relationship('Animal', backref='saude_registros')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TipoRacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco_kg = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(50), default='concentrado')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProducaoLeite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=True, index=True)
    litros = db.Column(db.Numeric(10, 2), nullable=False)
    gordura = db.Column(db.Numeric(5, 2))
    proteina = db.Column(db.Numeric(5, 2))
    ccs = db.Column(db.Numeric(10, 2))
    preco_venda = db.Column(db.Numeric(10, 4))
    total_receber = db.Column(db.Numeric(10, 2))
    data = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    animal = db.relationship('Animal', backref='producoes')

class ConsumoRacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False, index=True)
    tipo_racao_id = db.Column(db.Integer, db.ForeignKey('tipo_racao.id'), nullable=False, index=True)
    quantidade_kg = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False, index=True)
    custo = db.Column(db.Numeric(10, 2), nullable=False)
    eficiencia = db.Column(db.Numeric(10, 4))
    animal = db.relationship('Animal', backref='consumos')
    tipo_racao = db.relationship('TipoRacao', backref='consumos')

class PrecoLeite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    preco_litro = db.Column(db.Numeric(10, 4), nullable=False)
    data_vigencia = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Despesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    categoria = db.Column(db.String(50), index=True)
    data = db.Column(db.Date, nullable=False, index=True)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Orcamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50))
    valor_previsto = db.Column(db.Numeric(10, 2))
    valor_realizado = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    endereco = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vendas = db.relationship('VendaAvulsa', backref='cliente', lazy=True)

class VendaAvulsa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False, index=True)
    litros = db.Column(db.Numeric(10, 2), nullable=False)
    valor_litro = db.Column(db.Numeric(10, 4), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BackupLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    size_bytes = db.Column(db.Integer)
    checksum_sha256 = db.Column(db.String(64))
    record_count = db.Column(db.Integer)
    tables_info = db.Column(db.Text)
    status = db.Column(db.String(20), default='success')
    error_message = db.Column(db.Text)
    backup_type = db.Column(db.String(10), default='manual')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
