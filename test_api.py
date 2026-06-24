class TestAPI:
    def test_health(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'

    def test_clima(self, client):
        resp = client.get('/api/clima')
        assert resp.status_code == 200

    def test_cotacao_leite(self, client):
        resp = client.get('/api/cotacao-leite')
        assert resp.status_code == 200

    def test_atualizar_preco_anon(self, client):
        resp = client.post('/api/atualizar-preco', json={'preco': 3.50})
        assert resp.status_code == 401 or resp.status_code == 302
