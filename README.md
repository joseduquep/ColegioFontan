# 🏫 Colegio Fontán - Sistema de Horarios

Plataforma web para la gestión académica del Colegio Fontán. Permite a coordinadores y tutores administrar estudiantes, bloques, talleres y horarios de manera dinámica y automatizada.

> Sitio en producción: [https://horariosistemafontan.online](https://horariosistemafontan.online)

---

## 📌 Funcionalidades Principales

- Registro y gestión de estudiantes
- Asignación de talleres a estudiantes y tutores
- Generación automática de horarios y bloques
- Panel de control para seguimiento de tutorías
- Reportes académicos y administrativos
- Integración con **Celery** y **django-celery-beat** para tareas programadas como llamado a lista
- Generación de documentos PDF y QRs (asistencia, reportes)
- Administración a través del panel de Django (`/admin/`)

---

## 🛠️ Tecnologías y Dependencias

Proyecto desarrollado en **Django 5** y desplegado con **Gunicorn + Nginx** en **Linode**. Base de datos SQLite (por simplicidad y velocidad en entornos controlados).

### Principales librerías:

- **Celery 5.4.0** + **django-celery-beat**
- **pyHanko**, **xhtml2pdf**, **reportlab** para generación de documentos y firmas digitales
- **Pillow**, **qrcode**, **svglib** para contenido gráfico
- **Uvicorn**, **Whitenoise**, **gunicorn** para producción

> Ver el archivo `requirements.txt` para todas las dependencias detalladas.

---

## 🧪 Entornos

- `main`: Rama principal (producción)
- `dev`: Rama de desarrollo (local)
- `linode`: Rama de pruebas sobre servidor remoto (con datos reales y acceso restringido)

---

## 🚀 Despliegue

El proyecto está **disponible únicamente en línea**. No está pensado para uso local directo por usuarios externos.

En caso de pruebas locales por desarrolladores:
```bash
git clone https://github.com/joseduquep/ColegioFontan.git
cd ColegioFontan
git checkout dev
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
