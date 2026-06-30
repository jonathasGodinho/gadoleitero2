from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Animal, SaudeAnimal, ProducaoLeite, ConsumoRacao
from utils import log_auditoria
from datetime import datetime, date

animais_bp = Blueprint('animais', __name__)


@animais_bp.route('/animais', methods=['GET', 'POST'])
@login_required
def animais():
    if request.method == 'POST':
        nome = request.form.get('nome')
        brinco = request.form.get('brinco')
        if not brinco:
            ultimo = Animal.query.order_by(Animal.id.desc()).first()
            prox_id = (ultimo.id + 1) if ultimo else 1
            brinco = f'AUTO-{prox_id:04d}'
        else:
            brinco = brinco.strip()
            existente = Animal.query.filter_by(brinco=brinco).first()
            if existente:
                flash(f'Brinco "{brinco}" ja cadastrado para {existente.nome}', 'danger')
                return redirect(url_for('animais.animais'))
        raca = request.form.get('raca')
        lote = request.form.get('lote')
        sexo = request.form.get('sexo')
        status_reproducao = request.form.get('status_reproducao') or 'vazio'
        data_nascimento = datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date() if request.form.get('data_nascimento') else None
        data_ultima_inseminacao = datetime.strptime(request.form.get('data_ultima_inseminacao'), '%Y-%m-%d').date() if request.form.get('data_ultima_inseminacao') else None
        data_parto_prevista = datetime.strptime(request.form.get('data_parto_prevista'), '%Y-%m-%d').date() if request.form.get('data_parto_prevista') else None
        try:
            novo_animal = Animal(
                nome=nome, brinco=brinco, raca=raca, lote=lote,
                sexo=sexo,
                status_reproducao=status_reproducao,
                data_nascimento=data_nascimento,
                data_ultima_inseminacao=data_ultima_inseminacao,
                data_parto_prevista=data_parto_prevista
            )
            db.session.add(novo_animal)
            db.session.commit()
            log_auditoria('Animal cadastrado', f'{nome} - Brinco {brinco}')
            flash('Animal cadastrado!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar animal: {str(e)}', 'danger')
        return redirect(url_for('animais.animais'))
    
    busca = request.args.get('busca', '').strip()
    query = Animal.query
    if busca:
        like = f'%{busca}%'
        query = query.filter(
            db.or_(
                Animal.nome.ilike(like),
                Animal.brinco.ilike(like),
                Animal.raca.ilike(like),
                Animal.lote.ilike(like)
            )
        )
    page = request.args.get('page', 1, type=int)
    paginator = query.order_by(Animal.nome).paginate(page=page, per_page=50, error_out=False)
    return render_template('animais.html', animais=paginator.items, busca=busca, paginator=paginator)


@animais_bp.route('/animais/editar/<int:id>', methods=['POST'])
@login_required
def editar_animal(id):
    animal = Animal.query.get_or_404(id)
    animal.nome = request.form.get('nome', animal.nome)
    animal.raca = request.form.get('raca', animal.raca)
    animal.sexo = request.form.get('sexo', animal.sexo)
    animal.lote = request.form.get('lote', animal.lote)
    animal.ativo = request.form.get('ativo') == 'on'
    try:
        db.session.commit()
        log_auditoria('Animal editado', f'{animal.nome} - Brinco {animal.brinco}')
        flash('Animal atualizado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar animal: {str(e)}', 'danger')
    return redirect(url_for('animais.animais'))


@animais_bp.route('/animais/excluir/<int:id>')
@login_required
def excluir_animal(id):
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('animais.animais'))
    animal = Animal.query.get_or_404(id)
    try:
        SaudeAnimal.query.filter_by(animal_id=id).delete()
        ConsumoRacao.query.filter_by(animal_id=id).delete()
        ProducaoLeite.query.filter_by(animal_id=id).delete()
        db.session.delete(animal)
        db.session.commit()
        log_auditoria('Animal excluído', f'{animal.nome} - Brinco {animal.brinco}')
        flash('Animal excluído!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir animal: {str(e)}', 'danger')
    return redirect(url_for('animais.animais'))


@animais_bp.route('/animais/saude/<int:id>', methods=['GET', 'POST'])
@login_required
def saude_animal(id):
    animal = Animal.query.get_or_404(id)
    
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        descricao = request.form.get('descricao')
        data_aplicacao = datetime.strptime(request.form.get('data_aplicacao'), '%Y-%m-%d').date()
        proxima_dose = datetime.strptime(request.form.get('proxima_dose'), '%Y-%m-%d').date() if request.form.get('proxima_dose') else None
        custo = float(request.form.get('custo')) if request.form.get('custo') else None
        observacoes = request.form.get('observacoes')
        
        registro = SaudeAnimal(
            animal_id=id, tipo=tipo, descricao=descricao,
            data_aplicacao=data_aplicacao, proxima_dose=proxima_dose,
            custo=custo, observacoes=observacoes
        )
        db.session.add(registro)
        db.session.commit()
        log_auditoria('Registro saúde', f'Animal: {animal.nome}, Tipo: {tipo}')
        flash('Registro de saúde adicionado!', 'success')
        return redirect(url_for('animais.saude_animal', id=id))
    
    registros = SaudeAnimal.query.filter_by(animal_id=id).order_by(SaudeAnimal.data_aplicacao.desc()).all()
    from datetime import date
    return render_template('saude_animal.html', animal=animal, registros=registros, today=date.today())


@animais_bp.route('/saude/excluir/<int:id>')
@login_required
def excluir_saude(id):
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    registro = SaudeAnimal.query.get_or_404(id)
    animal_id = registro.animal_id
    db.session.delete(registro)
    db.session.commit()
    log_auditoria('Registro saúde excluído', f'ID {id}')
    flash('Registro de saúde excluído!', 'success')
    return redirect(url_for('animais.saude_animal', id=animal_id))
