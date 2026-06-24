from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Despesa, Orcamento
from utils import log_auditoria
from datetime import datetime, date

financeiro_bp = Blueprint('financeiro', __name__)


@financeiro_bp.route('/financeiro/editar/<int:id>', methods=['POST'])
@login_required
def editar_despesa(id):
    despesa = Despesa.query.get_or_404(id)
    despesa.descricao = request.form.get('descricao', despesa.descricao)
    despesa.categoria = request.form.get('categoria', despesa.categoria)
    despesa.valor = float(request.form.get('valor', despesa.valor))
    despesa.data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
    despesa.observacoes = request.form.get('observacoes', despesa.observacoes)
    db.session.commit()
    log_auditoria('Despesa editada', f'{despesa.descricao} - R$ {despesa.valor}')
    flash('Despesa atualizada!', 'success')
    return redirect(url_for('financeiro.financeiro'))


@financeiro_bp.route('/financeiro/excluir/<int:id>')
@login_required
def excluir_despesa(id):
    despesa = Despesa.query.get_or_404(id)
    db.session.delete(despesa)
    db.session.commit()
    log_auditoria('Despesa excluída', f'{despesa.descricao} - R$ {despesa.valor}')
    flash('Despesa excluída!', 'success')
    return redirect(url_for('financeiro.financeiro'))


@financeiro_bp.route('/financeiro', methods=['GET', 'POST'])
@login_required
def financeiro():
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        valor = float(request.form.get('valor'))
        categoria = request.form.get('categoria')
        data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()
        observacoes = request.form.get('observacoes')

        despesa = Despesa(
            descricao=descricao, valor=valor, categoria=categoria,
            data=data, observacoes=observacoes
        )
        db.session.add(despesa)
        db.session.commit()
        log_auditoria('Despesa registrada', f'{descricao} - R$ {valor}')
        flash('Despesa registrada!', 'success')
        return redirect(url_for('financeiro.financeiro'))

    filtro_data_ini = request.args.get('data_ini')
    filtro_data_fim = request.args.get('data_fim')
    filtro_categoria = request.args.get('categoria')

    query = Despesa.query
    if filtro_data_ini:
        query = query.filter(Despesa.data >= datetime.strptime(filtro_data_ini, '%Y-%m-%d').date())
    if filtro_data_fim:
        query = query.filter(Despesa.data <= datetime.strptime(filtro_data_fim, '%Y-%m-%d').date())
    if filtro_categoria:
        query = query.filter(Despesa.categoria == filtro_categoria)

    despesas = query.order_by(Despesa.data.desc()).all()

    total_despesas = sum(d.valor for d in despesas)

    return render_template('financeiro.html', despesas=despesas, total_despesas=total_despesas, today=date.today())


@financeiro_bp.route('/orcamento', methods=['GET', 'POST'])
@login_required
def orcamento():
    if request.method == 'POST':
        ano = int(request.form.get('ano'))
        mes = int(request.form.get('mes'))
        categoria = request.form.get('categoria')
        valor_previsto = float(request.form.get('valor_previsto'))
        valor_realizado = float(request.form.get('valor_realizado', 0))

        orcamento = Orcamento(
            ano=ano, mes=mes, categoria=categoria,
            valor_previsto=valor_previsto, valor_realizado=valor_realizado
        )
        db.session.add(orcamento)
        db.session.commit()
        log_auditoria('Orçamento cadastrado', f'{categoria} - {mes}/{ano}')
        flash('Orçamento cadastrado!', 'success')
        return redirect(url_for('financeiro.orcamento'))

    orcamentos = Orcamento.query.order_by(Orcamento.ano.desc(), Orcamento.mes).all()
    total_previsto = sum(o.valor_previsto for o in orcamentos)
    total_realizado = sum(o.valor_realizado for o in orcamentos)

    return render_template('orcamento.html',
                          orcamentos=orcamentos,
                          total_previsto=total_previsto,
                          total_realizado=total_realizado,
                          today=date.today())


@financeiro_bp.route('/orcamento/excluir/<int:id>')
@login_required
def excluir_orcamento(id):
    orcamento = Orcamento.query.get_or_404(id)
    db.session.delete(orcamento)
    db.session.commit()
    log_auditoria('Orçamento excluído', f'{orcamento.categoria} - {orcamento.mes}/{orcamento.ano}')
    flash('Orçamento excluído!', 'success')
    return redirect(url_for('financeiro.orcamento'))
