
# students/apps.py
from django.apps import AppConfig
from django.conf import settings



class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'students'

    def ready(self):
        print("Iniciando el programador...")  # Debug: Verifica si esto aparece
        from students.scheduler import start_scheduler
        start_scheduler()
