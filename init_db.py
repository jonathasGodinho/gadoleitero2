from app import app, db

def init_database():
    try:
        with app.app_context():
            db.create_all()
            print('Tabelas criadas via db.create_all()')

            from app import Animal, TipoRacao, PrecoLeite, User
            from datetime import date
            from werkzeug.security import generate_password_hash

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
                print('Admin criado: admin@terra-roxa.com / admin123')

            db.session.commit()
            print('Banco de dados inicializado!')
    except Exception as e:
        print(f'[init_db] Erro ao inicializar banco: {e}')