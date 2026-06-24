from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, AuditLog, ProducaoLeite, ConsumoRacao, Despesa, VendaAvulsa, SaudeAnimal, PrecoLeite, BackupLog
from utils import log_auditoria
from datetime import datetime, date
import json, re, os, hashlib
from pathlib import Path

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/ajustes')
@login_required
def ajustes():
    precos = PrecoLeite.query.order_by(PrecoLeite.data_vigencia.desc()).all()
    backups = BackupLog.query.order_by(BackupLog.created_at.desc()).limit(50).all()
    return render_template('ajustes.html', precos=precos, backups=backups)


@admin_bp.route('/ajustes/preco', methods=['POST'])
@login_required
def ajustar_preco():
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('admin.ajustes'))

    preco_litro = float(request.form.get('preco_litro'))
    data_vigencia = datetime.strptime(request.form.get('data_vigencia'), '%Y-%m-%d').date()

    novo_preco = PrecoLeite(preco_litro=preco_litro, data_vigencia=data_vigencia)
    db.session.add(novo_preco)
    db.session.commit()
    log_auditoria('Preço ajustado', f'R$ {preco_litro}/L a partir de {data_vigencia}')
    flash('Preço atualizado!', 'success')
    return redirect(url_for('admin.ajustes'))


@admin_bp.route('/ajustes/reset', methods=['POST'])
@login_required
def reset_dados():
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('admin.ajustes'))

    tipo = request.form.get('tipo', '')
    try:
        if tipo == 'producao':
            ProducaoLeite.query.delete()
            flash('Dados de produção limpos!', 'success')
        elif tipo == 'racao':
            ConsumoRacao.query.delete()
            flash('Dados de ração limpos!', 'success')
        elif tipo == 'todos':
            ProducaoLeite.query.delete()
            ConsumoRacao.query.delete()
            Despesa.query.delete()
            VendaAvulsa.query.delete()
            SaudeAnimal.query.delete()
            flash('Todos os dados foram limpos!', 'success')
        db.session.commit()
        log_auditoria('Reset dados', f'Tipo: {tipo}')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao limpar dados: {str(e)}', 'danger')
    return redirect(url_for('admin.ajustes'))


@admin_bp.route('/ajustes/restaurar', methods=['POST'])
@login_required
def ajustes_restaurar_backup():
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('admin.ajustes'))

    filename = request.form.get('filename')
    if not filename:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('admin.ajustes'))

    if not re.match(r'^[\w\-\.]+$', filename):
        flash('Nome de arquivo inválido', 'danger')
        return redirect(url_for('admin.ajustes'))

    from backup_util import restore_backup, BACKUP_DIR
    filepath = BACKUP_DIR / filename
    if not filepath.exists():
        flash('Arquivo de backup nao encontrado', 'danger')
        return redirect(url_for('admin.ajustes'))

    try:
        total = restore_backup(filename)
        log_auditoria('Backup restaurado', f'Arquivo: {filename} ({total} registros)')
        flash(f'Backup restaurado com sucesso! {total} registros recuperados.', 'success')
    except Exception as e:
        flash(f'Erro ao restaurar backup: {str(e)}', 'danger')

    return redirect(url_for('admin.ajustes'))


@admin_bp.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))

    usuarios = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_usuarios.html', usuarios=usuarios)


@admin_bp.route('/admin/usuario/criar', methods=['POST'])
@login_required
def admin_usuario_criar():
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    from werkzeug.security import generate_password_hash
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    is_admin = request.form.get('is_admin') == 'on'
    if User.query.filter_by(email=email).first():
        flash('Email já cadastrado', 'danger')
        return redirect(url_for('admin.admin_usuarios'))
    user = User(nome=nome, email=email, senha_hash=generate_password_hash(senha), is_admin=is_admin, role='admin' if is_admin else 'operador')
    db.session.add(user)
    db.session.commit()
    log_auditoria('Usuário criado', f'{email}')
    flash('Usuário criado!', 'success')
    return redirect(url_for('admin.admin_usuarios'))


@admin_bp.route('/admin/usuario/editar/<int:id>', methods=['POST'])
@login_required
def admin_usuario_editar(id):
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    from werkzeug.security import generate_password_hash
    user = User.query.get_or_404(id)
    user.nome = request.form.get('nome')
    user.email = request.form.get('email')
    senha = request.form.get('senha')
    if senha:
        user.senha_hash = generate_password_hash(senha)
    user.is_admin = request.form.get('is_admin') == 'on'
    user.role = 'admin' if user.is_admin else 'operador'
    db.session.commit()
    log_auditoria('Usuário editado', f'{user.email}')
    flash('Usuário atualizado!', 'success')
    return redirect(url_for('admin.admin_usuarios'))


@admin_bp.route('/admin/usuario/trocar-senha/<int:id>', methods=['POST'])
@login_required
def admin_usuario_trocar_senha(id):
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    from werkzeug.security import generate_password_hash
    user = User.query.get_or_404(id)
    nova_senha = request.form.get('nova_senha')
    user.senha_hash = generate_password_hash(nova_senha)
    db.session.commit()
    log_auditoria('Senha alterada', f'{user.email}')
    flash('Senha alterada!', 'success')
    return redirect(url_for('admin.admin_usuarios'))


@admin_bp.route('/admin/usuario/excluir/<int:id>')
@login_required
def admin_usuario_excluir(id):
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Você não pode excluir a si mesmo!', 'danger')
        return redirect(url_for('admin.admin_usuarios'))
    db.session.delete(user)
    db.session.commit()
    log_auditoria('Usuário excluído', f'{user.email}')
    flash('Usuário excluído!', 'success')
    return redirect(url_for('admin.admin_usuarios'))


@admin_bp.route('/admin/auditoria')
@login_required
def auditoria():
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('auditoria.html', logs=logs)


@admin_bp.route('/admin/backup')
@login_required
def backup_page():
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    from backup_util import get_backup_stats
    stats = get_backup_stats()
    return render_template('backup.html', stats=stats)


@admin_bp.route('/admin/backup/criar', methods=['POST'])
@login_required
def criar_backup():
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))

    from backup_util import perform_backup
    result = perform_backup(backup_type='manual')

    if result['status'] == 'success':
        log_auditoria('Backup manual criado', f'{result["filename"]} ({result["records"]} registros)')
        flash(result['message'], 'success')
    elif result['status'] == 'skipped':
        flash(result['message'], 'warning')
    else:
        flash(f'Erro: {result["message"]}', 'danger')

    return redirect(url_for('admin.backup_page'))


@admin_bp.route('/admin/backup/stats')
@login_required
def backup_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Acesso restrito'}), 403
    from backup_util import get_backup_stats
    return jsonify(get_backup_stats())


@admin_bp.route('/admin/backup/listar')
@login_required
def listar_backups():
    if current_user.role != 'admin':
        return jsonify([])
    logs = BackupLog.query.order_by(BackupLog.created_at.desc()).limit(100).all()
    return jsonify([{
        'id': l.id,
        'filename': l.filename,
        'size': l.size_bytes,
        'size_fmt': f"{l.size_bytes / 1024:.1f} KB" if l.size_bytes else '0 B',
        'date': l.created_at.strftime('%d/%m/%Y %H:%M') if l.created_at else '',
        'status': l.status,
        'records': l.record_count,
        'type': l.backup_type,
        'checksum': l.checksum_sha256
    } for l in logs])


@admin_bp.route('/admin/backup/download/<filename>')
@login_required
def download_backup(filename):
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    from backup_util import BACKUP_DIR
    filepath = BACKUP_DIR / filename
    if not filepath.exists():
        flash('Arquivo nao encontrado', 'danger')
        return redirect(url_for('admin.backup_page'))
    return send_file(str(filepath), as_attachment=True, download_name=filename)


@admin_bp.route('/admin/backup/verificar/<filename>')
@login_required
def verificar_backup(filename):
    if current_user.role != 'admin':
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))
    from backup_util import verify_backup
    result = verify_backup(filename)
    if result.get('error'):
        flash(f'Erro na verificacao: {result["error"]}', 'danger')
    elif result['valid']:
        match = '✓ checksum OK' if result.get('checksum_match') else '✓ integro (sem checksum armazenado)'
        flash(f'Backup verificado: {match}', 'success')
    else:
        flash('✗ Backup corrompido ou invalido', 'danger')
    return redirect(url_for('admin.backup_page'))


@admin_bp.route('/admin/backup/restaurar', methods=['POST'])
@login_required
def restaurar_backup():
    if current_user.role not in ['admin', 'gerente']:
        flash('Acesso restrito', 'danger')
        return redirect(url_for('geral.index'))

    filename = request.form.get('filename')
    if not filename:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('admin.backup_page'))

    if not re.match(r'^[\w\-\.]+$', filename):
        flash('Nome de arquivo invalido', 'danger')
        return redirect(url_for('admin.backup_page'))

    from backup_util import restore_backup, BACKUP_DIR
    filepath = BACKUP_DIR / filename
    if not filepath.exists():
        flash('Arquivo de backup nao encontrado', 'danger')
        return redirect(url_for('admin.backup_page'))

    try:
        total = restore_backup(filename)
        log_auditoria('Backup restaurado', f'Arquivo: {filename} ({total} registros)')
        flash(f'Backup restaurado com sucesso! {total} registros recuperados.', 'success')
    except Exception as e:
        flash(f'Erro ao restaurar backup: {str(e)}', 'danger')

    return redirect(url_for('admin.backup_page'))
