#!/bin/bash

# Ruta del proyecto y entorno virtual
PROJECT_DIR="/var/www/django_app/ColegioFontan/ColegioFontan"
VENV_DIR="/var/www/django_app/djangoenv"
GUNICORN_SERVICE="gunicorn"
NGINX_SERVICE="nginx"

echo "==> Cambiando al directorio del proyecto: $PROJECT_DIR"
cd $PROJECT_DIR

# Activar el entorno virtual
echo "==> Activando el entorno virtual..."
source $VENV_DIR/bin/activate

# Migraciones
echo "==> Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Recolección de archivos estáticos
echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar Gunicorn
echo "==> Reiniciando el servicio de Gunicorn..."
sudo systemctl restart $GUNICORN_SERVICE

# Reiniciar Nginx
echo "==> Reiniciando el servicio de Nginx..."
sudo systemctl restart $NGINX_SERVICE

# Confirmar servicios
echo "==> Confirmando el estado de Gunicorn..."
sudo systemctl status $GUNICORN_SERVICE | head -n 10

echo "==> Confirmando el estado de Nginx..."
sudo systemctl status $NGINX_SERVICE | head -n 10

echo "==> ¡Todo listo! Tu aplicación ha sido reiniciada correctamente. 🚀"
