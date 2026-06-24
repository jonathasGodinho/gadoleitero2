from datetime import date


class TestVendas:
    def test_vendas_page(self, client, login_admin):
        resp = client.get('/vendas-avulsas')
        assert resp.status_code == 200

    def test_create_cliente(self, client, login_admin):
        resp = client.post('/vendas-avulsas', data={
            'nome_cliente': 'Novo Cliente', 'telefone': '11988880001',
            'email': 'novo@teste.com', 'endereco': 'Rua X, 789',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_create_venda(self, client, login_admin):
        resp = client.post('/vendas-avulsas', data={
            'cliente_id': '1', 'litros': '100.0',
            'valor_litro': '3.20', 'data': date.today().strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_create_venda_invalid(self, client, login_admin):
        resp = client.post('/vendas-avulsas', data={
            'cliente_id': '1', 'litros': 'abc',
            'data': date.today().strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_venda(self, client, login_admin):
        resp = client.post('/vendas-avulsas/editar/1', data={
            'cliente_id': '1', 'litros': '120.0',
            'valor_litro': '3.10', 'data': date.today().strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_delete_venda(self, client, login_admin):
        resp = client.get('/vendas-avulsas/excluir/1', follow_redirects=True)
        assert resp.status_code == 200

    def test_delete_cliente(self, client, login_admin):
        resp = client.get('/vendas-avulsas/excluir-cliente/2', follow_redirects=True)
        assert resp.status_code == 200

    def test_export_pdf(self, client, login_admin):
        resp = client.get('/vendas-avulsas/exportar/pdf')
        assert resp.status_code == 200

    def test_export_excel(self, client, login_admin):
        resp = client.get('/vendas-avulsas/exportar/excel')
        assert resp.status_code == 200
