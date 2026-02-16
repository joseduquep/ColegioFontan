from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta
SECRET_KEY = 'django-insecure-oqd^oz@mj@5s!1!jw&xqj!g-ctw@g$0m&g1_9fq5xx__9tn482'

# DEBUG en producción
DEBUG = True  # Temporalmente True para debugging

# Configuración de hosts permitidos
ALLOWED_HOSTS = ['*']  # En producción, lista explícita de dominios.

# Origen confiable para CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://horariosistemafontan.online',
    'https://www.horariosistemafontan.online',
]

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Tus aplicaciones personalizadas
    'home',
    'accounts',
    'students',
    'tutors',
    'workshops',
    'schedules',
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de URLs
ROOT_URLCONF = 'horariosfontanproyecto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'horariosfontanproyecto/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'horariosfontanproyecto.wsgi.application'

# Base de datos
import os
import dj_database_url

# Configuración de base de datos
# Usa la variable de entorno DATABASE_URL (Neon/Producción)
# Si no existe, usa SQLite como fallback (Desarrollo local)
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://neondb_owner:npg_PIZhOrC6lS3g@ep-restless-glade-aiby47bw-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require'
)

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Archivos estáticos y media
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/django_app/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'horariosfontanproyecto/static'),
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de cookies y sesiones
SESSION_COOKIE_AGE = 10800  # Tiempo de sesión: 30 minutos
SESSION_COOKIE_HTTPONLY = True  # Bloquea acceso desde JavaScript
SESSION_COOKIE_SECURE = True  # Solo envía cookies por HTTPS
SESSION_COOKIE_SAMESITE = 'Strict'  # Restringe cookies a solicitudes del mismo sitio
SESSION_SAVE_EVERY_REQUEST = True  # Renueva la sesión en cada solicitud
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Cierra sesión al cerrar navegador

# Redirecciones después de login/logout
LOGIN_URL = '/login/'  # URL para redirección si no autenticado
LOGIN_REDIRECT_URL = '/profile/'  # URL después de iniciar sesión
LOGOUT_REDIRECT_URL = '/login/'  # URL después de cerrar sesión

# Seguridad adicional
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Configuración de logs (opcional, útil para debugging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
