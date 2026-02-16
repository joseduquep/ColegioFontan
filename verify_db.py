import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horariosfontanproyecto.settings')
django.setup()

from students.models import Student
from workshops.models import Workshop
from django.conf import settings

# Información de la base de datos
db_path = settings.DATABASES['default']['NAME']
print("=" * 80)
print("VERIFICACIÓN DE BASE DE DATOS")
print("=" * 80)
print(f"Base de datos en uso: {db_path}")
print()

# Estadísticas
total = Student.objects.count()
dummy = Student.objects.filter(name__icontains='dummy').count()
test = Student.objects.filter(name__icontains='test').count()
real = total - dummy - test

print(f"Total estudiantes: {total}")
print(f"Estudiantes con 'dummy': {dummy}")
print(f"Estudiantes con 'test': {test}")
print(f"Estudiantes reales: {real}")
print()

# Primeros 50 estudiantes
print("=" * 80)
print("PRIMEROS 50 ESTUDIANTES")
print("=" * 80)
students = Student.objects.all().order_by('student_id')[:50]
for s in students:
    workshop = s.workshop.name if s.workshop else "Sin taller"
    print(f"{s.student_id:4d} | {s.name:20s} | {s.lastname:20s} | {workshop:25s}")
