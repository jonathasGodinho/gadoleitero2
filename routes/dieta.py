from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Dieta, ItemDieta, Animal, TipoRacao
from utils import log_auditoria
from datetime import datetime, date

dieta_bp = Blueprint('dieta', __name__)


@dieta_bp.route('/dieta', methods=['GET', 'POST'])
@login_required
def dieta():
    if request.method == 'POST':
        animal_id = request.form.get('animal_id')
        nome = request.form.get('nome')
        data_inicio_str = request.form.get('data_inicio')
        data_fim_str = request.form.get('data_fim')
        observacoes = request.form.get('observacoes')

        if not animal_id or not nome or not data_inicio_str:
            flash('Preencha todos os campos obrigatórios', 'danger')
            return redirect(url_for('dieta.dieta'))

        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date() if data_fim_str else None
        except ValueError:
            flash('Data inválida', 'danger')
            return redirect(url_for('dieta.dieta'))

        try:
            dieta = Dieta(
                animal_id=int(animal_id), nome=nome,
                data_inicio=data_inicio, data_fim=data_fim,
                observacoes=observacoes
            )
            db.session.add(dieta)
            db.session.flush()

            tipos_racao = request.form.getlist('tipo_racao_id[]')
            quantidades = request.form.getlist('quantidade_kg[]')
            for tr_id, qtd in zip(tipos_racao, quantidades):
                if tr_id and qtd:
                    item = ItemDieta(
                        dieta_id=dieta.id,
                        tipo_racao_id=int(tr_id),
                        quantidade_kg_por_dia=float(qtd)
                    )
                    db.session.add(item)

            db.session.commit()
            log_auditoria('Dieta cadastrada', f'{nome} - Animal ID {animal_id}')
            flash('Dieta cadastrada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar dieta: {str(e)}', 'danger')
        return redirect(url_for('dieta.dieta'))

    page = request.args.get('page', 1, type=int)
    dietas_paginator = Dieta.query.order_by(Dieta.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    dietas = dietas_paginator.items
    animais = Animal.query.filter_by(ativo=True).order_by(Animal.nome).all()
    tipos_racao = TipoRacao.query.order_by(TipoRacao.nome).all()
    hoje = date.today()
    return render_template('dieta.html', dietas=dietas, paginator=dietas_paginator, animais=animais,
                           tipos_racao=tipos_racao, hoje=hoje)


@dieta_bp.route('/dieta/excluir/<int:id>')
@login_required
def excluir_dieta(id):
    dieta = Dieta.query.get_or_404(id)
    try:
        db.session.delete(dieta)
        db.session.commit()
        log_auditoria('Dieta excluída', f'{dieta.nome}')
        flash('Dieta excluída!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir dieta: {str(e)}', 'danger')
    return redirect(url_for('dieta.dieta'))
