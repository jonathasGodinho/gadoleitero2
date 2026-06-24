from datetime import date


class TestFinanceiro:
    def test_financeiro_page(self, client, login_admin):
        resp = client.get('/financeiro')
        assert resp.status_code == 200

    def test_create_despesa(self, client, login_admin):
        resp = client.post('/financeiro', data={
            'descricao': 'Nova despesa', 'valor': '500.00',
            'categoria': 'energia', 'data': date.today().strftime('%Y-%m-%d'),
            'observacoes': 'Teste',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_create_despesa_invalid(self, client, login_admin):
        resp = client.post('/financeiro', data={
            'descricao': 'Invalida', 'valor': 'abc',
            'data': date.today().strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_despesa(self, client, login_admin):
        resp = client.post('/financeiro/editar/1', data={
            'descricao': 'Despesa Editada', 'valor': '600.00',
            'categoria': 'pessoal', 'data': date.today().strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_delete_despesa(self, client, login_admin):
        resp = client.get('/financeiro/excluir/1', follow_redirects=True)
        assert resp.status_code == 200

    def test_orcamento_page(self, client, login_admin):
        resp = client.get('/orcamento')
        assert resp.status_code == 200

    def test_create_orcamento(self, client, login_admin):
        resp = client.post('/orcamento', data={
            'ano': date.today().year, 'mes': date.today().month,
            'categoria': 'energia', 'valor_previsto': '1500.00',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_delete_orcamento(self, client, login_admin):
        resp = client.get('/orcamento/excluir/1', follow_redirects=True)
        assert resp.status_code == 200
