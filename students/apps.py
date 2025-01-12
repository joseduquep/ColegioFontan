
# students/apps.py
from django.apps import AppConfig
from django.conf import settings

class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'students'

    def ready(self):
        if settings.DEBUG:  # Solo durante el desarrollo; elimina esto para producción
            from students.scheduler import start_scheduler
            start_scheduler()
