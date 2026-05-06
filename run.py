from app import app, db, User, PrecoLeite, Animal, TipoRacao
from datetime import date
from werkzeug.security import generate_password_hash
import os

with app.app_context():
    # Tentar usar migrações se disponível, senão usar create_all
    use_migrations = os.environ.get('FLASK_APP') and os.path.exists('migrations')
    
    if not use_migrations:
        db.create_all()
        print('Tabelas criadas via db.create_all()')
    
    # Criar dados iniciais se não existirem
    if not Animal.query.first():
        db.session.add(Animal(nome='Bella', brinco='001', raca='Holandesa', lote='Lote A'))
        db.session.add(Animal(nome='Mimosa', brinco='002', raca='Girolanda', lote='Lote A'))
        db.session.add(Animal(nome='Estrela', brinco='003', raca='Jersey', lote='Lote B'))
    
    if not TipoRacao.query.first():
        db.session.add(TipoRacao(nome='Ração Padrão', preco_kg=3.50, tipo='concentrado'))
        db.session.add(TipoRacao(nome='Ração Premium', preco_kg=5.00, tipo='concentrado'))
    
    if not PrecoLeite.query.first():
        db.session.add(PrecoLeite(preco_litro=2.50, data_vigencia=date(2024, 1, 1)))
    
    # Admin padrão
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
    print('✅ Banco de dados inicializado!')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f'Servidor iniciando na porta {port}...')
    app.run(host='0.0.0.0', port=port, debug=debug)
