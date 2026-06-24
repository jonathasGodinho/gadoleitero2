from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import ProducaoLeite, ConsumoRacao, Despesa, Animal, SaudeAnimal, PrecoLeite
from utils import get_preco_vigente, calcular_custo_producao, evolucao_custo_litro
from datetime import date, timedelta
from collections import defaultdict

geral_bp = Blueprint('geral', __name__)

@geral_bp.route('/offline')
@login_required
def offline():
    return render_template('offline.html')

@geral_bp.route('/')
@login_required
def index():
    today = date.today()
    
    # Métricas de hoje
    producoesHoje = ProducaoLeite.query.filter_by(data=today).all()
    total_litros = sum(p.litros for p in producoesHoje)
    num_animais_produzindo = len(set(p.animal_id for p in producoesHoje if p.animal_id))
    
    consumoHoje = ConsumoRacao.query.filter_by(data=today).all()
    total_custo_racao = sum(c.custo for c in consumoHoje)
    
    receita = 0
    for p in producoesHoje:
        preco = float(p.preco_venda) if p.preco_venda else float(get_preco_vigente(p.data))
        receita += float(p.litros) * preco
    
    lucro = receita - float(total_custo_racao)
    media_por_animal = total_litros / num_animais_produzindo if num_animais_produzindo > 0 else 0
    
    # Lucro mensal
    primeiro_dia_mes = date(today.year, today.month, 1)
    producoes_mes = ProducaoLeite.query.filter(ProducaoLeite.data >= primeiro_dia_mes).all()
    receita_mensal = 0
    for p in producoes_mes:
        preco = float(p.preco_venda) if p.preco_venda else float(get_preco_vigente(p.data))
        receita_mensal += float(p.litros) * preco
    custo_mensal = sum(c.custo for c in ConsumoRacao.query.filter(ConsumoRacao.data >= primeiro_dia_mes).all())
    lucro_mensal = receita_mensal - float(custo_mensal)
    
    # Últimos 7 dias
    ultimos_dias = []
    valores_producao = []
    custos_dia = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        ultimos_dias.append(d.strftime('%d/%m'))
        prods = ProducaoLeite.query.filter_by(data=d).all()
        valores_producao.append(sum(p.litros for p in prods))
        
        cons_dia = ConsumoRacao.query.filter_by(data=d).all()
        custos_dia.append(sum(c.custo for c in cons_dia))
    
    # Comparação com semana anterior
    semana_passada = []
    for i in range(13, 6, -1):
        d = date.today() - timedelta(days=i)
        prods = ProducaoLeite.query.filter_by(data=d).all()
        semana_passada.append(sum(p.litros for p in prods))
    
    total_semana_atual = sum(valores_producao)
    total_semana_passada = sum(semana_passada)
    variacao_semanal = ((total_semana_atual - total_semana_passada) / total_semana_passada * 100) if total_semana_passada > 0 else 0
    
    # Top 3 animais (maior produção na semana)
    from collections import defaultdict
    prod_por_animal = defaultdict(float)
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        prods = ProducaoLeite.query.filter_by(data=d).all()
        for p in prods:
            nome_animal = p.animal.nome if p.animal else 'Produção Geral'
            prod_por_animal[nome_animal] += float(p.litros)
    
    top_animais = sorted(prod_por_animal.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Tipos de ração mais consumidos (semana)
    racao_consumo = defaultdict(float)
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        cons = ConsumoRacao.query.filter_by(data=d).all()
        for c in cons:
            racao_consumo[c.tipo_racao.nome] += float(c.quantidade_kg)
    
    # Alertas de saúde (próximas vacinações/vermifugações)
    alertas_saude = SaudeAnimal.query.filter(
        SaudeAnimal.proxima_dose <= date.today() + timedelta(days=7),
        SaudeAnimal.proxima_dose >= date.today()
    ).all()
    
    custo_producao_hoje = calcular_custo_producao(today, today)
    
    custo_litro_dias, custo_litro_valores = evolucao_custo_litro(30)
    custo_litro_media = round(sum(custo_litro_valores) / len(custo_litro_valores), 4) if custo_litro_valores else 0
    
    # Resumo mensal de produção
    primeiro_dia_mes = date(today.year, today.month, 1)
    producoes_mes = ProducaoLeite.query.filter(ProducaoLeite.data >= primeiro_dia_mes).all()
    total_litros_mes = sum(p.litros for p in producoes_mes)
    receita_mensal = sum(float(p.litros) * float(p.preco_venda if p.preco_venda else get_preco_vigente(p.data)) for p in producoes_mes)
    
    # Produção mensal (últimos 12 meses)
    meses_labels = []
    valores_mensais = []
    for i in range(11, -1, -1):
        mes = today.month - i
        ano = today.year
        while mes < 1:
            mes += 12
            ano -= 1
        while mes > 12:
            mes -= 12
            ano += 1
        primeiro = date(ano, mes, 1)
        if mes == 12:
            ultimo = date(ano + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo = date(ano, mes + 1, 1) - timedelta(days=1)
        prods = ProducaoLeite.query.filter(ProducaoLeite.data >= primeiro, ProducaoLeite.data <= ultimo).all()
        meses_labels.append(date(ano, mes, 1).strftime('%m/%Y'))
        valores_mensais.append(sum(p.litros for p in prods))

    # Cotação atual do leite
    preco_vigente_hoje = get_preco_vigente(today)
    data_preco_vigente = PrecoLeite.query.filter(PrecoLeite.data_vigencia <= today).order_by(PrecoLeite.data_vigencia.desc()).first()
    data_cotacao = data_preco_vigente.data_vigencia.strftime('%d/%m/%Y') if data_preco_vigente else today.strftime('%d/%m/%Y')
    
    return render_template('index.html', 
                           total_litros=total_litros,
                           receita=receita,
                           custo=total_custo_racao,
                           lucro=lucro,
                           lucro_mensal=lucro_mensal,
                           media_por_animal=media_por_animal,
                           num_animais_produzindo=num_animais_produzindo,
                           dias=ultimos_dias,
                           valores_producao=valores_producao,
                           custos_dia=custos_dia,
                           variacao_semanal=variacao_semanal,
                           top_animais=top_animais,
                           racao_consumo=dict(racao_consumo),
                           alertas_saude=alertas_saude,
                           custo_producao=custo_producao_hoje,
                           total_animais=Animal.query.filter_by(ativo=True).count(),
                           preco_vigente=preco_vigente_hoje,
                           data_cotacao=data_cotacao,
                           total_litros_mes=total_litros_mes,
                           receita_mensal_resumo=receita_mensal,
                           receita_mensal=receita_mensal,
                           custo_litro_dias=custo_litro_dias,
                           custo_litro_valores=custo_litro_valores,
                            custo_litro_media=custo_litro_media,
                            meses_labels=meses_labels,
                            valores_mensais=valores_mensais)
