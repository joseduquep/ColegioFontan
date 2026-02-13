#!/bin/bash

NAME="horariosfontanproyecto"
SOCKFILE=/run/gunicorn.sock
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=horariosfontanproyecto.settings
DJANGO_WSGI_MODULE=horariosfontanproyecto.wsgi

echo "Starting $NAME as `whoami`"

# Activa el entorno virtual
source /var/www/django_app/djangoenv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=/var/www/django_app/ColegioFontan/ColegioFontan:$PYTHONPATH
umask 0007

# Inicia Gunicorn
exec /var/www/django_app/djangoenv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --capture-output
