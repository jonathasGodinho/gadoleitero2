from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(daemon=True)


def scheduled_backup_job():
    """Executado pelo scheduler. Cria backup automatico."""
    from backup_util import perform_backup
    logger.info('[scheduler] Iniciando backup automatico...')
    result = perform_backup(backup_type='auto')
    if result['status'] == 'success':
        logger.info(f'[scheduler] Backup OK: {result["filename"]}')
    elif result['status'] == 'skipped':
        logger.info(f'[scheduler] {result["message"]}')
    else:
        logger.error(f'[scheduler] Falha no backup: {result["message"]}')


def init_scheduler(app):
    """Inicializa o scheduler com backup diario as 02:00."""
    if scheduler.running:
        return

    scheduler.add_job(
        func=scheduled_backup_job,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_backup',
        name='Backup automatico diario',
        replace_existing=True,
        misfire_grace_time=3600
    )

    scheduler.start()
    logger.info('[scheduler] Backup automatico agendado: 02:00 todos os dias')

    atexit.register(lambda: scheduler.shutdown(wait=False))
