from django.apps import AppConfig
from django.db import connections
from django.db.utils import OperationalError
import time
from apscheduler.schedulers.background import BackgroundScheduler


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'

    # Variable pour éviter plusieurs démarrages
    scheduler_started = False

    def ready(self):
        self.wait_for_database()
        if not self.scheduler_started:  # Vérifiez si le planificateur est déjà démarré
            self.start_scheduler()
            AttendanceConfig.scheduler_started = True  # Marquez le planificateur comme démarré

    def wait_for_database(self, retries=5, delay=2):
        """
        Vérifie si la base de données est prête avant de continuer.
        """
        for _ in range(retries):
            try:
                connections['default'].cursor()
                print("Base de données prête.")
                return
            except OperationalError:
                print("Base de données non disponible, nouvelle tentative...")
                time.sleep(delay)
        raise OperationalError("Impossible de se connecter à la base de données après plusieurs tentatives.")

    def start_scheduler(self):
        """
        Démarre le planificateur.
        """
        from attendance.tasks import scheduler  # Importation différée
        scheduler.start()
        print("Planificateur démarré avec succès.")
    
    def stop_scheduler(self):
        """
        Arrête le planificateur proprement.
        """
        from attendance.tasks import scheduler  # Importation différée

        if scheduler.running:
            scheduler.shutdown()
            print("Planificateur arrêté proprement.")
