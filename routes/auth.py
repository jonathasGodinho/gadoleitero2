from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db, limiter
from models import User
from utils import log_auditoria
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('geral.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.ativo:
            if check_password_hash(user.senha_hash, password):
                login_user(user)
                log_auditoria('Login realizado', f'Usuário {email} fez login')
                return redirect(url_for('geral.index'))
        flash('Email ou senha inválidos', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'admin':
        flash('Acesso restrito a administradores', 'danger')
        return redirect(url_for('geral.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        nome = request.form.get('nome')
        senha = request.form.get('senha')
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'danger')
            return redirect(url_for('auth.register'))
        user = User(
            email=email, nome=nome,
            senha_hash=generate_password_hash(senha),
            is_admin=False, role='operador'
        )
        db.session.add(user)
        db.session.commit()
        log_auditoria('Usuário criado', f'Novo usuário: {email}')
        flash('Usuário criado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_auditoria('Logout realizado', f'Usuário {current_user.email} saiu')
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/minha-conta', methods=['GET', 'POST'])
@login_required
def minha_conta():
    if request.method == 'POST':
        current_user.nome = request.form.get('nome', current_user.nome)
        nova_senha = request.form.get('nova_senha')
        if nova_senha:
            current_user.senha_hash = generate_password_hash(nova_senha)
        db.session.commit()
        log_auditoria('Conta atualizada', f'Usuário {current_user.email} atualizou dados')
        flash('Dados atualizados!', 'success')
        return redirect(url_for('auth.minha_conta'))
    return render_template('minha_conta.html')
