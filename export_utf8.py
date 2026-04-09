import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horariosfontanproyecto.settings')
django.setup()

with open('backup_clean.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        natural_foreign=True,
        natural_primary=True,
        exclude=['contenttypes', 'auth.Permission', 'sessions', 'admin', 'students.Attendance'],
        indent=4,
        stdout=f
    )
print("Extraccion a backup_clean.json terminada.")
