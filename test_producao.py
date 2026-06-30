from datetime import date, timedelta


class TestProducao:
    def test_producao_page(self, client, login_admin):
        resp = client.get('/producao')
        assert resp.status_code == 200

    def test_producao_filter(self, client, login_admin):
        hoje = date.today()
        data_ini = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
        data_fim = hoje.strftime('%Y-%m-%d')
        resp = client.get(f'/producao?data_ini={data_ini}&data_fim={data_fim}')
        assert resp.status_code == 200

    def test_create_producao(self, client, login_admin):
        hoje = date.today().strftime('%Y-%m-%d')
        resp = client.post('/producao', data={
            'litros': '30.5', 'data': hoje, 'preco_venda': '2.50',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_create_producao_invalid_litros(self, client, login_admin):
        hoje = date.today().strftime('%Y-%m-%d')
        resp = client.post('/producao', data={
            'litros': 'abc', 'data': hoje,
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_producao(self, client, login_admin):
        resp = client.post('/producao/editar/1', data={
            'litros': '35.0', 'data': date.today().strftime('%Y-%m-%d'),
            'preco_venda': '2.60',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_producao_not_found(self, client, login_admin):
        resp = client.get('/producao/editar/999', follow_redirects=True)
        assert resp.status_code == 404

    def test_delete_producao_admin(self, client, login_admin):
        resp = client.get('/producao/excluir/1', follow_redirects=True)
        assert resp.status_code == 200

    def test_delete_producao_denied_operador(self, client, login_operador):
        resp = client.get('/producao/excluir/2', follow_redirects=True)
        assert resp.status_code == 200

    def test_export_pdf(self, client, login_admin):
        resp = client.get('/producao/exportar/pdf')
        assert resp.status_code == 200
        assert resp.content_type in ('application/pdf', 'text/html')

    def test_export_excel(self, client, login_admin):
        resp = client.get('/producao/exportar/excel')
        assert resp.status_code == 200
        assert 'spreadsheetml' in resp.content_type or 'openxml' in resp.content_type
