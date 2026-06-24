from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect
from extensions import db, csrf
from models import PrecoLeite
from utils import log_auditoria, get_preco_vigente
from datetime import date
import random
import requests

api_bp = Blueprint('api', __name__)


@api_bp.route('/health')
def health():
    return {'status': 'ok'}, 200


@api_bp.route('/api/clima')
@csrf.exempt
def api_clima():
    import requests
    WMO_CODES = {
        0: 'ceu limpo', 1: 'principalmente limpo', 2: 'parcialmente nublado', 3: 'nublado',
        45: 'nevoeiro', 48: 'nevoeiro denso',
        51: 'chuvisco leve', 53: 'chuvisco moderado', 55: 'chuvisco intenso',
        61: 'chuva leve', 63: 'chuva moderada', 65: 'chuva forte',
        66: 'chuva congelante leve', 67: 'chuva congelante forte',
        71: 'neve leve', 73: 'neve moderada', 75: 'neve intensa',
        77: 'graos de neve',
        80: 'pancadas de chuva leves', 81: 'pancadas de chuva moderadas', 82: 'pancadas de chuva violentas',
        85: 'pancadas de neve leves', 86: 'pancadas de neve intensas',
        95: 'tempestade', 96: 'tempestade com granizo leve', 99: 'tempestade com granizo forte'
    }
    WMO_ICONS = {
        0: '01d', 1: '02d', 2: '03d', 3: '04d',
        45: '50d', 48: '50d',
        51: '09d', 53: '09d', 55: '09d',
        61: '10d', 63: '10d', 65: '10d',
        66: '13d', 67: '13d',
        71: '13d', 73: '13d', 75: '13d', 77: '13d',
        80: '09d', 81: '09d', 82: '09d',
        85: '13d', 86: '13d',
        95: '11d', 96: '11d', 99: '11d'
    }
    try:
        LAT, LON = '-7.9268788', '-61.571846'
        url = f'https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code'
        resp = requests.get(url, timeout=5)
        data = resp.json()['current']
        code = data['weather_code']
        return {
            'temp': data['temperature_2m'],
            'description': WMO_CODES.get(code, 'nublado'),
            'humidity': data['relative_humidity_2m'],
            'icon': WMO_ICONS.get(code, '04d'),
            'location': 'Santo Antônio do Matupi - AM',
            'feels_like': data['apparent_temperature']
        }
    except Exception as e:
        current_app.logger.error(f'Erro ao buscar clima: {e}')
        return {'temp': 25, 'description': 'ensolarado', 'humidity': 60, 'icon': '01d', 'location': 'Santo Antônio do Matupi - AM', 'feels_like': 24}


@api_bp.route('/api/atualizar-preco', methods=['POST'])
@csrf.exempt
@login_required
def atualizar_preco():
    try:
        data = request.get_json()
        novo_preco = float(data.get('preco', 0))

        if novo_preco <= 0:
            return {'success': False, 'error': 'Preço inválido'}

        hoje = date.today()
        preco_existente = PrecoLeite.query.filter(PrecoLeite.data_vigencia <= hoje).order_by(PrecoLeite.data_vigencia.desc()).first()

        if preco_existente:
            preco_existente.preco_litro = novo_preco
        else:
            novo = PrecoLeite(data_vigencia=hoje, preco_litro=novo_preco)
            db.session.add(novo)

        db.session.commit()
        log_auditoria('Atualizar Preço Leite', f'Novo preço: R$ {novo_preco}')

        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@api_bp.route('/api/cotacao-leite')
@csrf.exempt
def api_cotacao_leite():
    try:
        hoje = date.today()
        preco = get_preco_vigente(hoje)
        preco_obj = PrecoLeite.query.filter(PrecoLeite.data_vigencia <= hoje).order_by(PrecoLeite.data_vigencia.desc()).first()
        data_cotacao = preco_obj.data_vigencia.strftime('%d/%m/%Y') if preco_obj else hoje.strftime('%d/%m/%Y')

        tendencia = 'alta' if random.random() > 0.5 else 'baixa'

        return {
            'preco': float(preco),
            'data': data_cotacao,
            'tendencia': tendencia
        }
    except Exception as e:
        current_app.logger.error(f'Erro ao buscar cotação: {e}')
        return {'preco': 2.50, 'data': date.today().strftime('%d/%m/%Y'), 'tendencia': 'estavel'}
