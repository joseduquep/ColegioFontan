#!/usr/bin/env python
"""
Script to re-export data from the SQLite backup with proper UTF-8 encoding.
Temporarily switches to the backup database, exports, then switches back.
"""
import os
import sys
import json

# Force UTF-8 output
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Temporarily override the DATABASE settings
os.environ['DATABASE_URL'] = ''  # Clear so it falls back

# We need to manually set up Django with the SQLite backup
import django
from django.conf import settings

# Override settings before setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horariosfontanproyecto.settings')

# Patch settings to use SQLite backup
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# We'll directly use SQLite via dumpdata
from django.core.management import call_command
from io import StringIO

# Override the database setting
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db_dev_backup_2026-02-13 (1).sqlite3',
}

django.setup()

# Close existing connections since we changed DB
from django import db
db.connections.close_all()

print("Exporting data from SQLite backup...")
output = StringIO()
call_command(
    'dumpdata',
    '--exclude', 'contenttypes',
    '--exclude', 'auth.Permission',
    '--indent', '2',
    stdout=output,
)
data = output.getvalue()

# Write with explicit UTF-8
with open('data_export.json', 'w', encoding='utf-8') as f:
    f.write(data)

print(f"Exported {len(data)} characters to data_export.json (UTF-8)")
print("Done!")
