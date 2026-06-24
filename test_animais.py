class TestAnimais:
    def test_animais_page(self, client, login_admin):
        resp = client.get('/animais')
        assert resp.status_code == 200

    def test_create_animal(self, client, login_admin):
        resp = client.post('/animais', data={
            'nome': 'Teste Animal', 'brinco': 'T099',
            'raca': 'Holandesa', 'sexo': 'femea', 'lote': 'Lote A',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_create_animal_duplicate_brinco(self, client, login_admin):
        resp = client.post('/animais', data={
            'nome': 'Outro', 'brinco': 'T099',
            'raca': 'Jersey', 'sexo': 'femea',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_animal(self, client, login_admin):
        resp = client.post('/animais/editar/1', data={
            'nome': 'Bella Editada', 'brinco': 'T001',
            'raca': 'Holandesa', 'sexo': 'femea', 'lote': 'Lote B',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_animal_not_found(self, client, login_admin):
        resp = client.post('/animais/editar/999', data={'nome': 'X', 'brinco': 'X99'}, follow_redirects=True)
        assert resp.status_code == 404

    def test_delete_animal_admin(self, client, login_admin):
        resp = client.get('/animais/excluir/2', follow_redirects=True)
        assert resp.status_code == 200

    def test_saude_page(self, client, login_admin):
        resp = client.get('/animais/saude/1')
        assert resp.status_code == 200

    def test_saude_add(self, client, login_admin):
        from datetime import date, timedelta
        hoje = date.today()
        resp = client.post('/animais/saude/1', data={
            'tipo': 'vacina', 'descricao': 'Febre aftosa',
            'data_aplicacao': (hoje - timedelta(days=1)).strftime('%Y-%m-%d'),
            'proxima_dose': (hoje + timedelta(days=180)).strftime('%Y-%m-%d'),
            'custo': '75.00',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_saude_delete(self, client, login_admin):
        resp = client.get('/saude/excluir/1', follow_redirects=True)
        assert resp.status_code == 200
