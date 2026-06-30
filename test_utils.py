from datetime import date, timedelta


class TestUtilsFunctions:
    def test_get_preco_vigente_exists(self, client, login_admin, app):
        with app.app_context():
            from utils import get_preco_vigente
            from models import PrecoLeite
            from extensions import db
            preco = PrecoLeite.query.first()
            result = get_preco_vigente(preco.data_vigencia)
            assert float(result) == 2.20

    def test_get_preco_vigente_fallback(self, client, login_admin, app):
        with app.app_context():
            from utils import get_preco_vigente
            result = get_preco_vigente(date(2020, 1, 1))
            assert float(result) > 0

    def test_calcular_custo_producao(self, client, login_admin, app):
        with app.app_context():
            from utils import calcular_custo_producao
            hoje = date.today()
            custo = calcular_custo_producao(hoje, hoje)
            assert custo >= 0

    def test_calcular_eficiencia_alimentar(self, client, login_admin, app):
        with app.app_context():
            from utils import calcular_eficiencia_alimentar
            from models import Animal
            animal = Animal.query.first()
            hoje = date.today()
            eficiencia = calcular_eficiencia_alimentar(animal.id, hoje, hoje)
            assert eficiencia >= 0

    def test_evolucao_custo_litro(self, client, login_admin, app):
        with app.app_context():
            from utils import evolucao_custo_litro
            dias, valores = evolucao_custo_litro(7)
            assert len(dias) == 7
            assert len(valores) == 7

    def test_evolucao_custo_litro_periodo(self, client, login_admin, app):
        with app.app_context():
            from utils import evolucao_custo_litro_periodo
            hoje = date.today()
            dias, valores = evolucao_custo_litro_periodo(hoje - timedelta(days=5), hoje)
            assert len(dias) == 6
            assert len(valores) == 6

    def test_log_auditoria(self, client, login_admin, app):
        with app.app_context():
            from utils import log_auditoria
            from models import AuditLog
            log_auditoria('Teste', 'Teste detalhes')
            logs = AuditLog.query.all()
            assert len(logs) > 0
            assert logs[-1].acao == 'Teste'
