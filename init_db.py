from app import app, db, Animal, TipoRacao, PrecoLeite, ProducaoLeite, ConsumoRacao, Despesa, Cliente, VendaAvulsa, User
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

def seed_animais():
    if Animal.query.first():
        return
    animais = [
        Animal(nome='Bella', brinco='001', raca='Holandesa', sexo='femea', lote='Lote A'),
        Animal(nome='Mimosa', brinco='002', raca='Girolanda', sexo='femea', lote='Lote A'),
        Animal(nome='Estrela', brinco='003', raca='Jersey', sexo='femea', lote='Lote B'),
        Animal(nome='Morena', brinco='004', raca='Holandesa', sexo='femea', lote='Lote A'),
        Animal(nome='Pintada', brinco='005', raca='Girolanda', sexo='femea', lote='Lote B'),
    ]
    db.session.add_all(animais)
    db.session.flush()
    print('Animais semeados')

def seed_producoes():
    if ProducaoLeite.query.first():
        return
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    dias = (hoje - primeiro_dia).days + 1
    for i in range(dias):
        d = hoje - timedelta(days=i)
        litros = 22.0 + (i * 0.3)
        db.session.add(ProducaoLeite(
            litros=litros, data=d,
            preco_venda=2.50, total_receber=litros * 2.50
        ))
    print(f'Producoes de leite semeadas ({dias} dias)')

def seed_racoes():
    if TipoRacao.query.first():
        return
    racoes = [
        TipoRacao(nome='Racao Padrao', preco_kg=3.50, tipo='concentrado'),
        TipoRacao(nome='Racao Premium', preco_kg=5.00, tipo='concentrado'),
        TipoRacao(nome='Racao Bezerro', preco_kg=4.20, tipo='crescimento'),
    ]
    db.session.add_all(racoes)
    print('Tipos de ração semeados')

def seed_precos():
    if PrecoLeite.query.first():
        return
    db.session.add(PrecoLeite(preco_litro=2.50, data_vigencia=date(2024, 1, 1)))
    print('Preco do leite semeado')

def seed_despesas():
    if Despesa.query.first():
        return
    despesas = [
        Despesa(descricao='Energia eletrica', valor=450.00, categoria='energia', data=date.today()),
        Despesa(descricao='Salario funcionario', valor=1500.00, categoria='pessoal', data=date.today()),
        Despesa(descricao='Vacina rebanho', valor=320.00, categoria='veterinario', data=date.today() - timedelta(days=5)),
        Despesa(descricao='Manutencao cercas', valor=280.00, categoria='manutencao', data=date.today() - timedelta(days=3)),
    ]
    db.session.add_all(despesas)
    print('Despesas semeadas')

def seed_clientes():
    if Cliente.query.first():
        return
    clientes = [
        Cliente(nome='Joao da Silva', telefone='(11) 99999-0001', endereco='Rua A, 123'),
        Cliente(nome='Maria Oliveira', telefone='(11) 99999-0002', endereco='Rua B, 456'),
    ]
    db.session.add_all(clientes)
    print('Clientes semeados')

def seed_admin():
    if User.query.filter_by(email='admin@terra-roxa.com').first():
        return
    admin = User(
        email='admin@terra-roxa.com',
        nome='Administrador',
        senha_hash=generate_password_hash('admin123'),
        is_admin=True,
        role='admin'
    )
    db.session.add(admin)
    print('Admin criado: admin@terra-roxa.com / admin123')

def init_database():
    try:
        with app.app_context():
            db.create_all()
            print('Tabelas criadas via db.create_all()')

            seed_animais()
            seed_producoes()
            seed_racoes()
            seed_precos()
            seed_despesas()
            seed_clientes()
            seed_admin()

            db.session.commit()
            print('Banco de dados inicializado com sucesso!')
    except Exception as e:
        print(f'[init_db] Erro ao inicializar banco: {e}')
