from extensions import db
from models import ProducaoLeite, ConsumoRacao, Despesa, PrecoLeite, SaudeAnimal, AuditLog
from flask import request
from flask_login import current_user
from datetime import date, timedelta

def log_auditoria(acao, detalhes='', user_id=None):
    if user_id is None and current_user.is_authenticated:
        user_id = current_user.id
    log = AuditLog(
        user_id=user_id,
        acao=acao,
        detalhes=detalhes,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

def get_preco_vigente(data_ref):
    preco = PrecoLeite.query.filter(PrecoLeite.data_vigencia <= data_ref).order_by(PrecoLeite.data_vigencia.desc()).first()
    return preco.preco_litro if preco else 0

def calcular_eficiencia_alimentar(animal_id, data_ini, data_fim):
    producoes = ProducaoLeite.query.filter(
        ProducaoLeite.animal_id == animal_id,
        ProducaoLeite.data >= data_ini,
        ProducaoLeite.data <= data_fim
    ).all()
    consumos = ConsumoRacao.query.filter(
        ConsumoRacao.animal_id == animal_id,
        ConsumoRacao.data >= data_ini,
        ConsumoRacao.data <= data_fim
    ).all()
    total_leite = sum(p.litros for p in producoes)
    total_racao = sum(c.quantidade_kg for c in consumos)
    return total_leite / total_racao if total_racao > 0 else 0

def calcular_custo_producao(data_ini, data_fim):
    producoes = ProducaoLeite.query.filter(
        ProducaoLeite.data >= data_ini,
        ProducaoLeite.data <= data_fim
    ).all()
    consumos = ConsumoRacao.query.filter(
        ConsumoRacao.data >= data_ini,
        ConsumoRacao.data <= data_fim
    ).all()
    despesas = Despesa.query.filter(
        Despesa.data >= data_ini,
        Despesa.data <= data_fim
    ).all()
    total_leite = sum(p.litros for p in producoes)
    total_custos = sum(c.custo for c in consumos) + sum(d.valor for d in despesas)
    return total_custos / total_leite if total_leite > 0 else 0

def evolucao_custo_litro(dias=30):
    arrays_datas, arrays_valores = [], []
    for i in range(dias - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        arrays_datas.append(d.strftime('%d/%m'))
        custo = calcular_custo_producao(d, d)
        arrays_valores.append(round(custo, 4))
    return arrays_datas, arrays_valores

def evolucao_custo_litro_periodo(data_ini, data_fim):
    arrays_datas, arrays_valores = [], []
    delta = (data_fim - data_ini).days
    if delta > 365:
        meses = sorted(set(
            [data_ini + timedelta(days=i) for i in range(delta + 1)]
        ), key=lambda x: x.strftime('%Y-%m'))
        meses_unicos = {}
        for i in range(delta + 1):
            d = data_ini + timedelta(days=i)
            mes_key = d.strftime('%Y-%m')
            if mes_key not in meses_unicos:
                meses_unicos[mes_key] = {'inicio': d}
        for mes_key in sorted(meses_unicos):
            m = meses_unicos[mes_key]
            primeiro = m['inicio']
            ultimo = (primeiro.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            if ultimo > data_fim:
                ultimo = data_fim
            arrays_datas.append(primeiro.strftime('%m/%Y'))
            custo = calcular_custo_producao(primeiro, ultimo)
            arrays_valores.append(round(custo, 4))
    else:
        for i in range(delta + 1):
            d = data_ini + timedelta(days=i)
            arrays_datas.append(d.strftime('%d/%m'))
            custo = calcular_custo_producao(d, d)
            arrays_valores.append(round(custo, 4))
    return arrays_datas, arrays_valores
