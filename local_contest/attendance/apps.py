from django.apps import AppConfig
from django.db import connections
from django.db.utils import OperationalError
import time
import logging

# Configuration des logs
logger = logging.getLogger(__name__)

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'

    # Variable pour éviter plusieurs démarrages
    scheduler_started = False

    def ready(self):
        try:
            self.wait_for_database()
            if not self.scheduler_started:  # Vérifiez si le planificateur est déjà démarré
                self.start_scheduler()
                AttendanceConfig.scheduler_started = True  # Marquez le planificateur comme démarré
        except OperationalError as e:
            logger.error(f"Erreur lors de l'initialisation de l'application : {e}")

    def wait_for_database(self, retries=5, delay=2):
        """
        Vérifie si la base de données est prête avant de continuer.
        """
        for attempt in range(1, retries + 1):
            try:
                connections['default'].cursor()
                logger.info("Base de données prête.")
                return
            except OperationalError:
                logger.warning(f"Tentative {attempt}/{retries} : Base de données non disponible, nouvelle tentative dans {delay} secondes...")
                time.sleep(delay)

        # Lever une erreur après toutes les tentatives échouées
        raise OperationalError("Impossible de se connecter à la base de données après plusieurs tentatives.")

    def start_scheduler(self):
        """
        Démarre le planificateur.
        """
        try:
            from attendance.tasks import scheduler  # Importation différée
            scheduler.start()
            logger.info("Planificateur démarré avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du planificateur : {e}")

    def stop_scheduler(self):
        """
        Arrête le planificateur proprement.
        """
        try:
            from attendance.tasks import scheduler  # Importation différée
            if scheduler.running:
                scheduler.shutdown()
                logger.info("Planificateur arrêté proprement.")
            else:
                logger.info("Le planificateur n'était pas en cours d'exécution.")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du planificateur : {e}")
