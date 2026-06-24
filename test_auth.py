from flask import url_for


class TestAuth:
    def test_login_page(self, client):
        resp = client.get('/login')
        assert resp.status_code == 200
        assert b'email' in resp.data.lower() or b'Login' in resp.data

    def test_login_success(self, client):
        resp = client.post('/login', data={'email': 'admin@teste.com', 'password': 'admin123'}, follow_redirects=True)
        assert resp.status_code == 200

    def test_login_invalid(self, client):
        resp = client.post('/login', data={'email': 'admin@teste.com', 'password': 'wrong'}, follow_redirects=True)
        assert resp.status_code == 200

    def test_logout(self, client, login_admin):
        resp = client.get('/logout', follow_redirects=True)
        assert resp.status_code == 200

    def test_register_page_admin(self, client, login_admin):
        resp = client.get('/register')
        assert resp.status_code == 200

    def test_register_denied_operador(self, client, login_operador):
        resp = client.get('/register', follow_redirects=True)
        assert resp.status_code == 200

    def test_minha_conta(self, client, login_admin):
        resp = client.get('/minha-conta')
        assert resp.status_code == 200

    def test_minha_conta_update(self, client, login_admin):
        resp = client.post('/minha-conta', data={'nome': 'Admin Atualizado'}, follow_redirects=True)
        assert resp.status_code == 200

    def test_index_redirect_anon(self, client):
        resp = client.get('/')
        assert resp.status_code == 302

    def test_index_authenticated(self, client, login_admin):
        resp = client.get('/')
        assert resp.status_code == 200
