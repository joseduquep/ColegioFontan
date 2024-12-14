from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Schedule
from students.models import Student
from workshops.models import Block, Workshop

def student_schedule(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    is_high_school = student.grade > 5

    # Definir horarios según el tipo de estudiante
    if is_high_school:
        schedule = {
            "Monday_Thursday": ["7:40-9:10", "9:40-11:00", "11:20-12:40", "1:20-2:40"],
            "Friday": ["7:40-9:10", "9:50-11:20", "11:50-1:20"],
        }
        workshops = Workshop.objects.filter(type__in=['high_school', 'collective'])
    else:
        schedule = {
            "Monday_Thursday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:30-1:30", "1:50-2:40"],
            "Friday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:20-1:20"],
        }
        workshops = Workshop.objects.filter(type__in=['primary', 'collective'])

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    num_blocks = range(1, len(schedule["Monday_Thursday"]) + 1)

    # Recuperar horarios del estudiante
    student_schedule = Schedule.objects.filter(student=student).select_related('block')

    # Organizar datos en una estructura amigable para la plantilla
    schedule_table = []
    for block_number in num_blocks:
        row = []
        for day in days_of_week:
            workshop_name = None
            for entry in student_schedule:
                if entry.block.block_number == block_number and entry.block.day == day:
                    workshop_name = entry.block.workshop.name
                    break
            row.append({
                "day": day,
                "block_number": block_number,
                "workshop": workshop_name,
            })
        schedule_table.append(row)

    context = {
        "student": student,
        "schedule_table": schedule_table,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
        "workshops": workshops,
    }

    return render(request, "schedules/schedule.html", context)


def select_workshop(request, student_id, day, block_number):
    student = get_object_or_404(Student, student_id=student_id)

    # Determinar qué talleres mostrar basado en el grado del estudiante
    is_high_school = student.grade > 5
    if is_high_school:
        workshops = Workshop.objects.filter(type__in=['high_school', 'collective'])
    else:
        workshops = Workshop.objects.filter(type__in=['primary', 'collective'])

    if request.method == "POST":
        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)

        # Recuperar el bloque correspondiente usando el taller y el número de bloque
        block_obj = get_object_or_404(
            Block,
            block_number=block_number,
            day=day,
            workshop=workshop
        )

        # Verificar capacidad del taller
        current_capacity = Schedule.objects.filter(block=block_obj).count()
        if current_capacity >= workshop.max_capacity:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'workshops': workshops,
                'day': day,
                'block': block_number,
                'error': 'El taller seleccionado ha alcanzado su capacidad máxima.',
            })

        # Crear la programación del taller
        schedule_entry = Schedule.objects.create(
            student=student,
            block=block_obj
        )

        # Agregar el estudiante al bloque
        block_obj.students.add(student)

        # Redirigir al horario del estudiante
        return HttpResponseRedirect(reverse('student_schedule', args=[student_id]))

    return render(request, 'schedules/select_workshop.html', {
        'student': student,
        'workshops': workshops,
        'day': day,
        'block': block_number,
    })
