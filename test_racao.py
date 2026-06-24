from datetime import date


class TestRacao:
    def test_racao_page(self, client, login_admin):
        resp = client.get('/racao')
        assert resp.status_code == 200

    def test_create_tipo_racao(self, client, login_admin):
        resp = client.post('/racao', data={
            'nome': 'Racao Teste C', 'preco_kg': '4.50', 'tipo': 'concentrado',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_delete_tipo_racao(self, client, login_admin):
        resp = client.get('/racao/excluir/1', follow_redirects=True)
        assert resp.status_code == 200

    def test_consumo_page(self, client, login_admin):
        resp = client.get('/racao/consumo')
        assert resp.status_code == 200

    def test_create_consumo(self, client, login_admin):
        resp = client.post('/racao/consumo', data={
            'animal_id': '1', 'tipo_racao_id': '1',
            'quantidade_kg': '15.0', 'data': date.today().strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_create_consumo_invalid(self, client, login_admin):
        resp = client.post('/racao/consumo', data={
            'animal_id': '1', 'tipo_racao_id': '1',
            'quantidade_kg': 'abc', 'data': date.today().strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_delete_consumo(self, client, login_admin):
        resp = client.get('/racao/consumo/excluir/1', follow_redirects=True)
        assert resp.status_code == 200
