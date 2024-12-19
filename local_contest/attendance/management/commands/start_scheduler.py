from django.core.management.base import BaseCommand
from attendance.tasks import scheduler

class Command(BaseCommand):
    help = 'Démarre le planificateur APScheduler'

    def handle(self, *args, **kwargs):
        scheduler.start()
        self.stdout.write(self.style.SUCCESS('Le planificateur a démarré avec succès.'))
