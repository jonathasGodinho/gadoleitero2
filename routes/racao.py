from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import TipoRacao, ConsumoRacao, Animal, ProducaoLeite
from utils import log_auditoria
from datetime import datetime, date

racao_bp = Blueprint('racao', __name__)


@racao_bp.route('/racao', methods=['GET', 'POST'])
@login_required
def racao():
    if request.method == 'POST':
        nome = request.form.get('nome')
        preco_kg = float(request.form.get('preco_kg'))
        tipo = request.form.get('tipo', 'concentrado')

        novo_tipo = TipoRacao(nome=nome, preco_kg=preco_kg, tipo=tipo)
        db.session.add(novo_tipo)
        db.session.commit()
        log_auditoria('Tipo ração cadastrado', f'{nome} - R$ {preco_kg}/kg')
        flash('Tipo de ração cadastrado!', 'success')
        return redirect(url_for('racao.racao'))

    tipos = TipoRacao.query.all()
    return render_template('racao.html', tipos=tipos)


@racao_bp.route('/racao/excluir/<int:id>')
@login_required
def excluir_racao(id):
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('racao.racao'))
    tipo = TipoRacao.query.get_or_404(id)
    db.session.delete(tipo)
    db.session.commit()
    log_auditoria('Tipo ração excluído', f'{tipo.nome}')
    flash('Tipo de ração excluído!', 'success')
    return redirect(url_for('racao.racao'))


@racao_bp.route('/racao/consumo/excluir/<int:id>')
@login_required
def excluir_consumo_racao(id):
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('racao.consumo_racao'))
    consumo = ConsumoRacao.query.get_or_404(id)
    db.session.delete(consumo)
    db.session.commit()
    log_auditoria('Consumo ração excluído', f'ID {id}')
    flash('Consumo excluído!', 'success')
    return redirect(url_for('racao.consumo_racao'))


@racao_bp.route('/racao/consumo', methods=['GET', 'POST'])
@login_required
def consumo_racao():
    if request.method == 'POST':
        animal_id = request.form.get('animal_id')
        tipo_racao_id = request.form.get('tipo_racao_id')
        quantidade_kg = float(request.form.get('quantidade_kg'))
        data = datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()

        tipo = TipoRacao.query.get(tipo_racao_id)
        custo = quantidade_kg * float(tipo.preco_kg)
        eficiencia = None
        if quantidade_kg > 0:
            producao_dia = ProducaoLeite.query.filter_by(animal_id=animal_id, data=data).first()
            if producao_dia:
                eficiencia = float(producao_dia.litros) / quantidade_kg

        novo_consumo = ConsumoRacao(
            animal_id=animal_id, tipo_racao_id=tipo_racao_id,
            quantidade_kg=quantidade_kg, data=data, custo=custo,
            eficiencia=eficiencia
        )
        db.session.add(novo_consumo)
        db.session.commit()
        log_auditoria('Consumo registrado', f'Animal ID {animal_id}, {quantidade_kg}kg')
        flash('Consumo registrado!', 'success')
        return redirect(url_for('racao.consumo_racao'))

    animais = Animal.query.filter_by(ativo=True).all()
    tipos = TipoRacao.query.all()
    filtro_data_ini = request.args.get('data_ini')
    filtro_data_fim = request.args.get('data_fim')

    query = ConsumoRacao.query
    if filtro_data_ini:
        query = query.filter(ConsumoRacao.data >= datetime.strptime(filtro_data_ini, '%Y-%m-%d').date())
    if filtro_data_fim:
        query = query.filter(ConsumoRacao.data <= datetime.strptime(filtro_data_fim, '%Y-%m-%d').date())

    consumos = query.order_by(ConsumoRacao.data.desc()).all()

    today = date.today().strftime('%Y-%m-%d')
    return render_template('consumo_racao.html', animais=animais, tipos=tipos, consumos=consumos, today=today)
