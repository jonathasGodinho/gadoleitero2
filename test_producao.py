from app import app

with app.test_client() as client:
    client.post('/login', data={'email': 'admin@terra-roxa.com', 'password': 'admin123'})
    resp = client.get('/producao')
    html = resp.data.decode()
    
    print('=== STATUS ===')
    print('HTTP Status:', resp.status_code)
    
    print('\n=== MODAL CHECK ===')
    print('Button data-bs-toggle present:', 'data-bs-toggle="modal"' in html)
    print('Button data-bs-target present:', 'data-bs-target="#novaProducaoModal"' in html)
    print('Modal div present:', 'id="novaProducaoModal"' in html)
    print('Modal class fade:', 'modal fade' in html)
    print('Bootstrap JS loaded:', 'bootstrap.bundle.min.js' in html)
    
    print('\n=== HTML STRUCTURE ===')
    open_divs = html.count('<div')
    close_divs = html.count('</div>')
    print(f'Open divs: {open_divs}')
    print(f'Close divs: {close_divs}')
    print(f'Balance: {open_divs - close_divs}')
    
    print('\n=== FORM FIELDS ===')
    print('animal_id select:', 'name="animal_id"' in html)
    print('litros input:', 'name="litros"' in html)
    print('preco_venda input:', 'name="preco_venda"' in html)
    print('data input:', 'name="data"' in html)
    print('form method POST:', '<form method="POST">' in html)
