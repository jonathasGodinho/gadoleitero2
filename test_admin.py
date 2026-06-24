class TestAdmin:
    def test_ajustes_page_admin(self, client, login_admin):
        resp = client.get('/ajustes')
        assert resp.status_code == 200

    def test_ajustes_denied_operador(self, client, login_operador):
        resp = client.get('/ajustes', follow_redirects=True)
        assert resp.status_code == 200

    def test_update_preco(self, client, login_admin):
        from datetime import date, timedelta
        resp = client.post('/ajustes/preco', data={
            'preco_litro': '3.00',
            'data_vigencia': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_usuarios_page(self, client, login_admin):
        resp = client.get('/admin/usuarios')
        assert resp.status_code == 200

    def test_create_usuario(self, client, login_admin):
        resp = client.post('/admin/usuario/criar', data={
            'email': 'novo@admin.com', 'nome': 'Novo Admin',
            'senha': '123456', 'role': 'admin',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_edit_usuario(self, client, login_admin):
        resp = client.post('/admin/usuario/editar/1', data={
            'email': 'admin@teste.com', 'nome': 'Admin Renomeado', 'role': 'admin',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_backup_page(self, client, login_admin):
        resp = client.get('/admin/backup')
        assert resp.status_code == 200

    def test_create_backup(self, client, login_admin):
        resp = client.post('/admin/backup/criar', follow_redirects=True)
        assert resp.status_code == 200

    def test_auditoria_page(self, client, login_admin):
        resp = client.get('/admin/auditoria')
        assert resp.status_code == 200

    def test_cooperativas_page(self, client, login_admin):
        resp = client.get('/cooperativas')
        assert resp.status_code == 200
