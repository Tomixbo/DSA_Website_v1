from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJobExecution
from apscheduler.schedulers.background import BackgroundScheduler
from attendance.models import AttendanceCode
from attendance.utils import code_generator
from datetime import timedelta
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

def generate_attendance_code():
    """
    Génère un nouveau code de présence et supprime l'ancien.
    """
    try:
        AttendanceCode.objects.all().delete()
        new_code = code_generator()
        AttendanceCode.objects.create(code=new_code)
        logger.info(f"Nouveau code généré : {new_code}")
    except Exception as e:
        logger.error(f"Erreur lors de la génération du code de présence : {e}")

def delete_old_job_executions(max_age=3600):
    """
    Supprime les exécutions de job qui ont plus d'une heure (3600 secondes).
    """
    try:
        cutoff_time = now() - timedelta(seconds=max_age)
        deleted_count, _ = DjangoJobExecution.objects.filter(run_time__lt=cutoff_time).delete()
        logger.info(f"{deleted_count} anciennes exécutions de jobs supprimées.")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des anciennes exécutions de jobs : {e}")

# Configuration du planificateur
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

# Ajout de la tâche de génération de code
scheduler.add_job(
    generate_attendance_code,
    "interval",
    seconds=30,
    id="attendance.tasks.scheduled_job",
    replace_existing=True,
)

# Ajout de la tâche de nettoyage
scheduler.add_job(
    delete_old_job_executions,
    "interval",
    minutes=10,
    id="attendance.tasks.cleanup_job_executions",
    replace_existing=True,
)

register_events(scheduler)
