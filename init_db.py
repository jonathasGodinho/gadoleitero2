from app import app, db, Animal, TipoRacao, PrecoLeite, ProducaoLeite, ConsumoRacao, Despesa, Cliente, User
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

def init_database():
    try:
        with app.app_context():
            db.create_all()
            print('Tabelas criadas via db.create_all()')

            if not Animal.query.first():
                animais = [
                    Animal(nome='Bella', brinco='001', raca='Holandesa', sexo='femea', lote='Lote A'),
                    Animal(nome='Mimosa', brinco='002', raca='Girolanda', sexo='femea', lote='Lote A'),
                    Animal(nome='Estrela', brinco='003', raca='Jersey', sexo='femea', lote='Lote B'),
                    Animal(nome='Morena', brinco='004', raca='Holandesa', sexo='femea', lote='Lote A'),
                    Animal(nome='Pintada', brinco='005', raca='Girolanda', sexo='femea', lote='Lote B'),
                ]
                db.session.add_all(animais)
                db.session.flush()

                for i in range(10):
                    d = date.today() - timedelta(days=i)
                    db.session.add(ProducaoLeite(
                        litros=25.0 + (i * 0.5), data=d,
                        preco_venda=2.50, total_receber=(25.0 + (i * 0.5)) * 2.50
                    ))
                print('Produções de leite semeadas')

            if not TipoRacao.query.first():
                racoes = [
                    TipoRacao(nome='Racao Padrao', preco_kg=3.50, tipo='concentrado'),
                    TipoRacao(nome='Racao Premium', preco_kg=5.00, tipo='concentrado'),
                    TipoRacao(nome="Racao Bezerro", preco_kg=4.20, tipo='crescimento'),
                ]
                db.session.add_all(racoes)
                print('Tipos de ração semeados')

            if not PrecoLeite.query.first():
                db.session.add(PrecoLeite(preco_litro=2.50, data_vigencia=date(2024, 1, 1)))
                print('Preço do leite semeado')

            if not Despesa.query.first():
                despesas = [
                    Despesa(descricao='Energia eletrica', valor=450.00, categoria='energia', data=date.today()),
                    Despesa(descricao='Salario funcionario', valor=1500.00, categoria='pessoal', data=date.today()),
                    Despesa(descricao='Vacina rebanho', valor=320.00, categoria='veterinario', data=date.today() - timedelta(days=5)),
                    Despesa(descricao='Manutencao cercas', valor=280.00, categoria='manutencao', data=date.today() - timedelta(days=3)),
                ]
                db.session.add_all(despesas)
                print('Despesas semeadas')

            if not Cliente.query.first():
                clientes = [
                    Cliente(nome='Joao da Silva', telefone='(11) 99999-0001', endereco='Rua A, 123'),
                    Cliente(nome='Maria Oliveira', telefone='(11) 99999-0002', endereco='Rua B, 456'),
                ]
                db.session.add_all(clientes)
                print('Clientes semeados')

            if not User.query.filter_by(email='admin@terra-roxa.com').first():
                admin = User(
                    email='admin@terra-roxa.com',
                    nome='Administrador',
                    senha_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    role='admin'
                )
                db.session.add(admin)
                print('Admin criado: admin@terra-roxa.com / admin123')

            db.session.commit()
            print('Banco de dados inicializado com sucesso!')
    except Exception as e:
        print(f'[init_db] Erro ao inicializar banco: {e}')
