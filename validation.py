import re
from datetime import date


ERROS = {
    'required': 'O campo {} é obrigatorio.',
    'maxlen': 'O campo {} deve ter no maximo {} caracteres.',
    'email': 'Formato de email invalido.',
    'telefone': 'Formato de telefone invalido. Use (XX) XXXXX-XXXX.',
    'positive': 'O valor deve ser maior que zero.',
    'min_value': 'O valor minimo é {}.',
    'max_value': 'O valor maximo é {}.',
    'date_future': 'A data nao pode ser no futuro.',
    'date_past': 'A data nao pode ser no passado.',
    'invalid_date': 'Data invalida.',
}


def validate_required(value, field_name):
    if not value or not str(value).strip():
        return ERROS['required'].format(field_name)
    return None


def validate_maxlen(value, field_name, maxlen=200):
    if value and len(str(value)) > maxlen:
        return ERROS['maxlen'].format(field_name, maxlen)
    return None


def validate_email(email):
    if not email:
        return None
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email.strip()):
        return ERROS['email']
    return validate_maxlen(email, 'Email', 150)


def validate_telefone(telefone):
    if not telefone:
        return None
    digits = re.sub(r'\D', '', telefone)
    if len(digits) < 10 or len(digits) > 11:
        return ERROS['telefone']
    return None


def validate_positive(value, field_name):
    try:
        val = float(value)
        if val <= 0:
            return ERROS['positive']
    except (ValueError, TypeError):
        return ERROS['positive']
    return None


def validate_min(value, field_name, minimo=0):
    try:
        val = float(value)
        if val < minimo:
            return ERROS['min_value'].format(minimo)
    except (ValueError, TypeError):
        return f'O campo {field_name} deve ser numerico.'
    return None


def validate_max(value, field_name, maximo=999999):
    try:
        val = float(value)
        if val > maximo:
            return ERROS['max_value'].format(maximo)
    except (ValueError, TypeError):
        return f'O campo {field_name} deve ser numerico.'
    return None


def validate_date_not_future(data_str, field_name='Data'):
    try:
        d = _parse_date(data_str)
        if d > date.today():
            return ERROS['date_future']
    except (ValueError, TypeError):
        return ERROS['invalid_date']
    return None


def validate_date_not_past(data_str, field_name='Data'):
    try:
        d = _parse_date(data_str)
        if d < date.today():
            return ERROS['date_past']
    except (ValueError, TypeError):
        return ERROS['invalid_date']
    return None


def validate_date_range(data_str, field_name='Data'):
    try:
        d = _parse_date(data_str)
        if d < date(2000, 1, 1) or d > date(2100, 12, 31):
            return 'Data fora do intervalo valido (2000-2100).'
    except (ValueError, TypeError):
        return ERROS['invalid_date']
    return None


def validate_nome(nome):
    err = validate_required(nome, 'Nome')
    if err:
        return err
    return validate_maxlen(nome, 'Nome', 200)


def validate_descricao(desc):
    if not desc:
        return None
    return validate_maxlen(desc, 'Descricao', 500)


def _parse_date(data_str):
    if isinstance(data_str, date):
        return data_str
    from datetime import datetime
    return datetime.strptime(data_str, '%Y-%m-%d').date()


def validate_all(rules, form):
    """Aplica multiplas validacoes. Retorna lista de (campo, erro)."""
    erros = []
    for campo, validators in rules:
        valor = form.get(campo)
        for v in validators:
            if callable(v):
                erro = v(valor)
            else:
                nome_campo = v.get('field', campo)
                fn = v['validator']
                kwargs = {k: v for k, v in v.items() if k not in ('validator', 'field')}
                erro = fn(valor, **kwargs)
            if erro:
                erros.append((campo, erro))
                break
    return erros
