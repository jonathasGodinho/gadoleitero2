import os
import json
import hashlib
import tarfile
import io
from datetime import datetime, date, timedelta
from pathlib import Path

BACKUP_DIR = Path(__file__).parent / 'backups'
TABLE_NAMES = [
    'animal', 'tipo_racao', 'producao_leite', 'consumo_racao',
    'preco_leite', 'despesa', 'orcamento', 'user', 'audit_log',
    'cliente', 'venda_avulsa', 'saude_animal'
]
TABLE_ORDER = [
    'user', 'animal', 'tipo_racao', 'preco_leite', 'cliente',
    'producao_leite', 'consumo_racao', 'despesa', 'orcamento',
    'venda_avulsa', 'saude_animal', 'audit_log'
]
DAILY_KEEP = 7
WEEKLY_KEEP = 4
MONTHLY_KEEP = 12


def _collect_data():
    """Extrai dados de todas as tabelas, retorna dict com contagens."""
    from app import db
    backup_data = {}
    counts = {}
    for table_name in TABLE_NAMES:
        try:
            table = db.metadata.tables.get(table_name)
            if table is None:
                continue
            rows = db.session.execute(table.select()).fetchall()
            backup_data[table_name] = [dict(row._mapping) for row in rows]
            counts[table_name] = len(backup_data[table_name])
        except Exception:
            backup_data[table_name] = []
            counts[table_name] = 0
    return backup_data, counts


def _compute_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build_tar_gz(data: dict, counts: dict) -> tuple[bytes, str, int]:
    """Gera .tar.gz em memória. Retorna (bytes, checksum, total_records)."""
    metadata = {
        'version': '2.0',
        'created_at': datetime.utcnow().isoformat(),
        'table_counts': counts,
        'total_records': sum(counts.values())
    }
    data_json = json.dumps(data, ensure_ascii=False, indent=2, default=str).encode('utf-8')
    meta_json = json.dumps(metadata, ensure_ascii=False, indent=2).encode('utf-8')

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        info_data = tarfile.TarInfo(name='data.json')
        info_data.size = len(data_json)
        tar.addfile(info_data, io.BytesIO(data_json))

        info_meta = tarfile.TarInfo(name='metadata.json')
        info_meta.size = len(meta_json)
        tar.addfile(info_meta, io.BytesIO(meta_json))

    raw = buf.getvalue()
    checksum = _compute_checksum(raw)
    total_records = sum(counts.values())
    return raw, checksum, total_records


def _classify_backup(filename: str) -> str:
    """Classifica backup como daily / weekly / monthly."""
    stem = filename.replace('backup_terra_roxa_', '').replace('.tar.gz', '')
    try:
        d = datetime.strptime(stem[:8], '%Y%m%d').date()
    except ValueError:
        return 'daily'
    today = date.today()
    is_monday = d.weekday() == 0
    is_first_day = d.day == 1
    age_days = (today - d).days

    if is_first_day and age_days <= MONTHLY_KEEP * 31:
        return 'monthly'
    if is_monday and age_days <= WEEKLY_KEEP * 7:
        return 'weekly'
    return 'daily'


def perform_backup(backup_type='manual', description=''):
    """Gera um backup .tar.gz com checksum e registra no log.

    Retorna dict com resultado ou dict com erro.
    """
    from app import db
    from extensions import db as ext_db
    from models import BackupLog

    try:
        data, counts = _collect_data()
        has_data = any(v for v in counts.values())
        if not has_data:
            return {'status': 'skipped', 'message': 'Nenhum dado para backup'}

        raw_bytes, checksum, total_records = _build_tar_gz(data, counts)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_terra_roxa_{timestamp}.tar.gz'
        filepath = BACKUP_DIR / filename

        BACKUP_DIR.mkdir(exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(raw_bytes)

        with open(filepath.with_suffix('.sha256'), 'w') as f:
            f.write(f'{checksum}  {filename}')

        log_entry = BackupLog(
            filename=filename,
            size_bytes=len(raw_bytes),
            checksum_sha256=checksum,
            record_count=total_records,
            tables_info=json.dumps(counts),
            status='success',
            backup_type=backup_type
        )
        ext_db.session.add(log_entry)
        ext_db.session.commit()

        _apply_retention()

        return {
            'status': 'success',
            'filename': filename,
            'size': len(raw_bytes),
            'checksum': checksum,
            'records': total_records,
            'message': f'Backup {filename} criado com sucesso ({total_records} registros)'
        }
    except Exception as e:
        try:
            log_entry = BackupLog(
                filename='error',
                status='failed',
                error_message=str(e),
                backup_type=backup_type
            )
            ext_db.session.add(log_entry)
            ext_db.session.commit()
        except Exception:
            pass
        return {'status': 'failed', 'message': str(e)}


def _apply_retention():
    """Remove backups baseado em política de retenção.

    Mantém:
    - Últimos DAILY_KEEP backups diários
    - Últimos WEEKLY_KEEP backups semanais (segunda-feira)
    - Últimos MONTHLY_KEEP backups mensais (dia 1)
    """
    all_files = sorted(BACKUP_DIR.glob('backup_terra_roxa_*.tar.gz'), reverse=True)

    keep = set()
    daily_count = 0
    weekly_count = 0
    monthly_count = 0

    for fp in all_files:
        cls = _classify_backup(fp.name)
        if cls == 'monthly' and monthly_count < MONTHLY_KEEP:
            keep.add(fp.name)
            monthly_count += 1
        elif cls == 'weekly' and weekly_count < WEEKLY_KEEP:
            keep.add(fp.name)
            weekly_count += 1
        elif cls == 'daily' and daily_count < DAILY_KEEP:
            keep.add(fp.name)
            daily_count += 1

    for fp in all_files:
        if fp.name not in keep:
            fp.unlink(missing_ok=True)
            sha = fp.with_suffix('.sha256')
            sha.unlink(missing_ok=True)


def verify_backup(filename: str) -> dict:
    """Verifica a integridade de um backup .tar.gz ou .json."""
    filepath = BACKUP_DIR / filename
    if not filepath.exists():
        return {'valid': False, 'error': 'Arquivo nao encontrado'}

    try:
        raw = filepath.read_bytes()
        computed = _compute_checksum(raw)

        sha_path = filepath.with_suffix('.sha256')
        stored = ''
        if sha_path.exists():
            stored = sha_path.read_text().strip().split()[0]

        is_old_json = filepath.suffix == '.json'
        if is_old_json:
            data = json.loads(raw.decode('utf-8'))
            total = sum(len(v) for v in data.values())
            return {
                'valid': True,
                'checksum_match': computed == stored if stored else None,
                'checksum_computed': computed,
                'checksum_stored': stored or None,
                'has_data_json': True,
                'has_metadata_json': False,
                'total_records': total,
                'table_counts': {k: len(v) for k, v in data.items()},
                'created_at': None,
                'size_bytes': len(raw),
                'format': 'json (legado)'
            }

        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
            members = tar.getnames()
            has_data = 'data.json' in members
            has_meta = 'metadata.json' in members
            meta = json.loads(tar.extractfile('metadata.json').read()) if has_meta else {}

        return {
            'valid': computed == stored if stored else True,
            'checksum_match': computed == stored if stored else None,
            'checksum_computed': computed,
            'checksum_stored': stored or None,
            'has_data_json': has_data,
            'has_metadata_json': has_meta,
            'total_records': meta.get('total_records'),
            'table_counts': meta.get('table_counts'),
            'created_at': meta.get('created_at'),
            'size_bytes': len(raw),
            'format': 'tar.gz'
        }
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def _load_backup_data(filepath: Path) -> dict:
    """Carrega dados de backup .tar.gz ou .json (retrocompativel)."""
    raw = filepath.read_bytes()
    if filepath.suffix == '.json':
        return json.loads(raw.decode('utf-8'))
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        if 'data.json' not in tar.getnames():
            raise ValueError('Backup invalido: data.json nao encontrado')
        return json.loads(tar.extractfile('data.json').read())


def restore_backup(filename: str) -> int:
    """Restaura dados de um backup .tar.gz ou .json. Substitui todos os dados atuais."""
    from sqlalchemy import DateTime, Date, Numeric, Boolean
    from app import db

    filepath = BACKUP_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f'Backup {filename} nao encontrado')

    try:
        backup_data = _load_backup_data(filepath)
    except Exception as e:
        raise ValueError(f'Erro ao ler backup: {e}')

    def parse_value(val, col):
        if val is None:
            return None
        col_type = col.type
        if isinstance(col_type, DateTime):
            if isinstance(val, str):
                for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        return datetime.strptime(val, fmt)
                    except Exception:
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
        for table_name in reversed(TABLE_ORDER):
            table = db.metadata.tables.get(table_name)
            if table is not None:
                conn.execute(table.delete())

        total = 0
        for table_name in TABLE_ORDER:
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


def _migrate_old_json_backups():
    """Descobre backups .json antigos e registra no BackupLog."""
    from models import BackupLog
    from extensions import db

    existing = {l.filename for l in BackupLog.query.with_entities(BackupLog.filename).all()}
    for fp in sorted(BACKUP_DIR.glob('backup_terra_roxa_*.json')):
        if fp.name not in existing:
            try:
                data = json.loads(fp.read_text(encoding='utf-8'))
                total = sum(len(v) for v in data.values())
                entry = BackupLog(
                    filename=fp.name,
                    size_bytes=fp.stat().st_size,
                    record_count=total,
                    tables_info=json.dumps({k: len(v) for k, v in data.items()}),
                    status='success',
                    backup_type='auto',
                    created_at=datetime.fromtimestamp(fp.stat().st_mtime)
                )
                db.session.add(entry)
            except Exception:
                pass
    db.session.commit()


def get_backup_stats() -> dict:
    """Retorna estatísticas dos backups para o dashboard."""
    from models import BackupLog
    from extensions import db

    _migrate_old_json_backups()
    logs = BackupLog.query.order_by(BackupLog.created_at.desc()).all()
    total = len(logs)
    success = sum(1 for l in logs if l.status == 'success')
    failed = sum(1 for l in logs if l.status == 'failed')
    total_size = sum(l.size_bytes or 0 for l in logs)

    last = logs[0] if logs else None
    last_info = None
    if last:
        last_info = {
            'filename': last.filename,
            'size': last.size_bytes,
            'date': last.created_at.strftime('%d/%m/%Y %H:%M'),
            'status': last.status,
            'records': last.record_count,
            'checksum': last.checksum_sha256
        }

    recent = []
    for l in logs[:20]:
        recent.append({
            'id': l.id,
            'filename': l.filename,
            'size': l.size_bytes,
            'date': l.created_at.strftime('%d/%m/%Y %H:%M'),
            'status': l.status,
            'records': l.record_count,
            'type': l.backup_type
        })

    calendar_data = {}
    for l in logs:
        day = l.created_at.strftime('%Y-%m-%d')
        if day not in calendar_data:
            calendar_data[day] = {'status': l.status, 'count': 1}
        elif l.status == 'failed':
            calendar_data[day]['status'] = 'failed'
            calendar_data[day]['count'] += 1
        else:
            calendar_data[day]['count'] += 1

    return {
        'total': total,
        'success': success,
        'failed': failed,
        'total_size_bytes': total_size,
        'last_backup': last_info,
        'recent': recent,
        'calendar': calendar_data,
        'daily_keep': DAILY_KEEP,
        'weekly_keep': WEEKLY_KEEP,
        'monthly_keep': MONTHLY_KEEP
    }
