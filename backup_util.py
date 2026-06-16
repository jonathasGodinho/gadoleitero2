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
