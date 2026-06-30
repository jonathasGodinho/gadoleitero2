from datetime import date, timedelta
from flask import url_for


class TestRelatorios:
    def test_relatorios_page(self, client, login_admin):
        resp = client.get('/relatorios')
        assert resp.status_code == 200

    def test_relatorios_filter(self, client, login_admin):
        hoje = date.today()
        primeiro = hoje.replace(day=1)
        resp = client.get(f'/relatorios?data_ini={primeiro}&data_fim={hoje}')
        assert resp.status_code == 200

    def test_relatorios_vendas(self, client, login_admin):
        hoje = date.today()
        primeiro = hoje.replace(day=1)
        resp = client.get(f'/relatorios?data_ini={primeiro}&data_fim={hoje}&tipo=vendas-avulsas')
        assert resp.status_code == 200

    def test_relatorios_pdf(self, client, login_admin):
        hoje = date.today()
        primeiro = hoje.replace(day=1)
        resp = client.get(f'/relatorios/pdf?data_ini={primeiro}&data_fim={hoje}')
        assert resp.status_code == 200
        assert resp.headers['Content-Type'] in ('application/pdf', 'text/html')

    def test_relatorios_excel(self, client, login_admin):
        hoje = date.today()
        primeiro = hoje.replace(day=1)
        resp = client.get(f'/relatorios/excel?data_ini={primeiro}&data_fim={hoje}')
        assert resp.status_code == 200
        assert 'application/vnd.openxmlformats' in resp.headers['Content-Type']

    def test_cooperativas(self, client, login_admin):
        resp = client.get('/cooperativas')
        assert resp.status_code == 200

    def test_relatorios_redirect_anon(self, client):
        resp = client.get('/relatorios')
        assert resp.status_code == 302
