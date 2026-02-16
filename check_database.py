#!/usr/bin/env python
"""
Script para verificar el contenido de la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horariosfontanproyecto.settings')
django.setup()

from students.models import Student
from workshops.models import Workshop, Block
from tutors.models import Tutor
from schedules.models import Schedule
from django.conf import settings

def main():
    print("=" * 100)
    print("VERIFICACIÓN DE BASE DE DATOS - HorariosFontan 3.0")
    print("=" * 100)
    print(f"\n📁 Base de datos en uso: {settings.DATABASES['default']['NAME']}")
    print(f"🔧 Motor: {settings.DATABASES['default']['ENGINE']}")
    
    # Estadísticas generales
    print("\n" + "=" * 100)
    print("📊 ESTADÍSTICAS GENERALES")
    print("=" * 100)
    
    total_students = Student.objects.count()
    total_workshops = Workshop.objects.count()
    total_blocks = Block.objects.count()
    total_tutors = Tutor.objects.count()
    total_schedules = Schedule.objects.count()
    
    print(f"👥 Total Estudiantes: {total_students}")
    print(f"🏫 Total Talleres: {total_workshops}")
    print(f"📅 Total Bloques: {total_blocks}")
    print(f"👨‍🏫 Total Tutores: {total_tutors}")
    print(f"🗓️  Total Horarios: {total_schedules}")
    
    # Verificar estudiantes dummy/test
    print("\n" + "=" * 100)
    print("🔍 ANÁLISIS DE DATOS")
    print("=" * 100)
    
    dummy_students = Student.objects.filter(name__icontains='dummy').count()
    test_students = Student.objects.filter(name__icontains='test').count()
    real_students = Student.objects.exclude(name__icontains='dummy').exclude(name__icontains='test').count()
    
    print(f"🤖 Estudiantes con 'dummy': {dummy_students}")
    print(f"🧪 Estudiantes con 'test': {test_students}")
    print(f"✅ Estudiantes reales: {real_students}")
    
    # Distribución por grado
    print("\n" + "=" * 100)
    print("📚 DISTRIBUCIÓN POR GRADO")
    print("=" * 100)
    
    grades = Student.objects.values_list('grade', flat=True).distinct().order_by('grade')
    for grade in grades:
        count = Student.objects.filter(grade=grade).count()
        grade_name = dict(Student._meta.get_field('grade').choices).get(grade, str(grade))
        print(f"Grado {grade_name}: {count} estudiantes")
    
    # Mostrar TODOS los estudiantes
    print("\n" + "=" * 100)
    print(f"📋 LISTA COMPLETA DE ESTUDIANTES ({total_students} registros)")
    print("=" * 100)
    print(f"{'ID':<6} | {'Nombre':<25} | {'Apellido':<25} | {'Cédula':<12} | {'Grado':<15} | {'Taller':<20}")
    print("-" * 130)
    
    students = Student.objects.all().order_by('grade', 'lastname', 'name')
    for s in students:
        grade_name = dict(Student._meta.get_field('grade').choices).get(s.grade, str(s.grade))
        workshop_name = s.workshop.name if s.workshop else "Sin asignar"
        print(f"{s.student_id:<6} | {s.name:<25} | {s.lastname:<25} | {s.id_number:<12} | {grade_name:<15} | {workshop_name:<20}")
    
    # Resumen de talleres
    print("\n" + "=" * 100)
    print("🏫 RESUMEN DE TALLERES")
    print("=" * 100)
    print(f"{'ID':<6} | {'Nombre':<30} | {'Tipo':<15} | {'Tutor':<25} | {'Estudiantes':<12}")
    print("-" * 100)
    
    workshops = Workshop.objects.all().order_by('name')
    for w in workshops:
        tutor_name = str(w.tutor.user.get_full_name() or w.tutor.user.username) if w.tutor else "Sin asignar"
        student_count = Student.objects.filter(workshop=w).count()
        type_name = dict(Workshop._meta.get_field('type').choices).get(w.type, w.type)
        print(f"{w.workshop_id:<6} | {w.name:<30} | {type_name:<15} | {tutor_name:<25} | {student_count:<12}")
    
    print("\n" + "=" * 100)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 100)

if __name__ == '__main__':
    main()
