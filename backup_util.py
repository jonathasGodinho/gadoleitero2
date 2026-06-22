import os
import json
from datetime import datetime, timedelta
from pathlib import Path

BACKUP_DIR = Path(__file__).parent / 'backups'
MAX_BACKUPS = 30  # manter últimos 30 backups

def auto_backup(app, db):
    with app.app_context():
        backup_data = {}
        for table_name in ['animal', 'tipo_racao', 'producao_leite', 'consumo_racao',
                           'preco_leite', 'despesa', 'orcamento', 'user', 'audit_log',
                           'cliente', 'venda_avulsa', 'saude_animal']:
            try:
                table = db.metadata.tables.get(table_name)
                if table is None:
                    continue
                rows = db.session.execute(table.select()).fetchall()
                backup_data[table_name] = [dict(row._mapping) for row in rows]
            except Exception:
                backup_data[table_name] = []
        
        has_data = any(len(v) > 0 for v in backup_data.values())
        if not has_data:
            return None
        
        BACKUP_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_terra_roxa_{timestamp}.json'
        filepath = BACKUP_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        _rotate_backups()
        
        from flask import current_app
        current_app.logger.info(f'Backup automatico salvo: {filename}')
        return str(filepath)

def should_daily_backup():
    BACKUP_DIR.mkdir(exist_ok=True)
    today_prefix = datetime.now().strftime('%Y%m%d')
    for f in sorted(BACKUP_DIR.glob('backup_terra_roxa_*.json'), reverse=True):
        if today_prefix in f.name:
            return False
    return True

def get_latest_backup():
    BACKUP_DIR.mkdir(exist_ok=True)
    backups = sorted(BACKUP_DIR.glob('backup_terra_roxa_*.json'), reverse=True)
    return backups[0] if backups else None

def list_backups():
    BACKUP_DIR.mkdir(exist_ok=True)
    backups = sorted(BACKUP_DIR.glob('backup_terra_roxa_*.json'), reverse=True)
    result = []
    for f in backups:
        size = f.stat().st_size
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        result.append({'filename': f.name, 'size': size, 'date': mtime})
    return result

def _rotate_backups():
    backups = sorted(BACKUP_DIR.glob('backup_terra_roxa_*.json'), reverse=True)
    for f in backups[MAX_BACKUPS:]:
        f.unlink()

def restore_backup(filename):
    from sqlalchemy import DateTime, Date, Numeric, Boolean
    filepath = BACKUP_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f'Backup {filename} nao encontrado')

    with open(filepath, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    from app import db
    table_order = [
        'user', 'animal', 'tipo_racao', 'preco_leite', 'cliente',
        'producao_leite', 'consumo_racao', 'despesa', 'orcamento',
        'venda_avulsa', 'saude_animal', 'audit_log',
    ]

    def parse_value(val, col):
        if val is None:
            return None
        col_type = col.type
        if isinstance(col_type, DateTime):
            if isinstance(val, str):
                for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        return datetime.strptime(val, fmt)
                    except:
                        pass
            return val
        if isinstance(col_type, Date):
            if isinstance(val, str):
                return datetime.strptime(val, '%Y-%m-%d').date()
            return val
        if isinstance(col_type, Boolean):
            if isinstance(val, str):
                return val.lower() in ('true', '1', 'yes')
            return bool(val)
        if isinstance(col_type, Numeric):
            if isinstance(val, str):
                return float(val)
            return val
        return val

    conn = db.engine.connect()
    trans = conn.begin()
    try:
        for table_name in reversed(table_order):
            table = db.metadata.tables.get(table_name)
            if table is not None:
                conn.execute(table.delete())

        total = 0
        for table_name in table_order:
            rows = backup_data.get(table_name, [])
            if not rows:
                continue
            table = db.metadata.tables.get(table_name)
            if table is None:
                continue
            for row in rows:
                parsed = {}
                for k, v in row.items():
                    if k in table.columns:
                        parsed[k] = parse_value(v, table.columns[k])
                    else:
                        parsed[k] = v
                conn.execute(table.insert().values(parsed))
            total += len(rows)

        trans.commit()
        conn.close()
        return total
    except Exception as e:
        trans.rollback()
        conn.close()
        raise e
