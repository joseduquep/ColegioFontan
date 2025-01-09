from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Schedule
from students.models import Student
from workshops.models import Block, Workshop
from tutors.models import Tutor
import logging

# Configuración básica de logging
logger = logging.getLogger(__name__)


# Función auxiliar: Determinar horario y talleres disponibles
def get_schedule_and_workshops(student_or_tutor):
    schedule = {
        "Monday_Thursday": ["7:40-9:10", "9:40-11:00", "11:20-12:40", "1:20-2:40"]
        if student_or_tutor.grade > 5
        else ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:30-1:30", "1:50-2:40"],
        "Friday": ["7:40-9:10", "9:50-11:20", "11:50-1:20"]
        if student_or_tutor.grade > 5
        else ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:20-1:20"],
    }
    workshop_types = ['high_school', 'collective'] if student_or_tutor.grade > 5 else ['primary', 'collective']
    workshops = Workshop.objects.filter(type__in=workshop_types)
    return schedule, workshops


def student_schedule(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    schedule, workshops = get_schedule_and_workshops(student)

    # Si se pasa el workshop_id en la URL, actualizar el taller base
    workshop_id = request.GET.get('workshop_id')
    if workshop_id:
        try:
            workshop = Workshop.objects.get(id=workshop_id)
            student.workshop = workshop
            student.save()
        except Workshop.DoesNotExist:
            pass

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    num_blocks = range(1, len(schedule["Monday_Thursday"]) + 1)
    student_schedule = Schedule.objects.filter(student=student).select_related('block')

    schedule_table = [
        [
            {
                "day": day,
                "block_number": block_number,
                "workshop": next(
                    (entry.block.workshop.name for entry in student_schedule
                     if entry.block.block_number == block_number and entry.block.day == day),
                    None
                ),
            }
            for day in days_of_week
        ]
        for block_number in num_blocks
    ]

    context = {
        "student": student,
        "schedule_table": schedule_table,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
        "workshops": workshops,
    }

    return render(request, "schedules/student_schedule.html", context)


def get_block_capacity(workshops, day, block_number):
    for workshop in workshops:
        block = Block.objects.filter(workshop=workshop, day=day, block_number=block_number).first()
        workshop.current_capacity = block.students.count() if block else 0


def select_workshop(request, student_id, day, block_number):
    student = get_object_or_404(Student, student_id=student_id)
    _, workshops = get_schedule_and_workshops(student)
    get_block_capacity(workshops, day, block_number)

    if request.method == "POST":
        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
        block = Block.objects.filter(block_number=block_number, day=day, workshop=workshop).first()

        if not block or block.students.count() >= workshop.max_capacity:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'student_id': student_id,
                'workshops': workshops,
                'day': day,
                'block': block_number,
                'error': 'Bloque no encontrado o capacidad máxima alcanzada.',
            })

        Schedule.objects.filter(student=student, block__day=day, block__block_number=block_number).delete()
        Schedule.objects.create(student=student, block=block)
        block.students.add(student)

        return HttpResponseRedirect(reverse('student_schedule', args=[student_id]))

    return render(request, 'schedules/select_workshop.html', {
        'student': student,
        'student_id': student_id,
        'workshops': workshops,
        'day': day,
        'block': block_number,
    })


@login_required
def select_block(request, tutor_id, day, block_number):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    blocks = Block.objects.filter(day=day, block_number=block_number)

    return render(request, 'schedules/students_by_block.html', {
        'tutor': tutor,
        'blocks': blocks,
        'day': day,
        'block_number': block_number,
    })


@login_required
def students_in_block(request, tutor_id, day, block_number):
    print("funcion students_in_block funcionando")
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    block = Block.objects.filter(
        workshop__tutor=tutor,
        day=day,
        block_number=block_number).first()

    if not block:
        raise Http404("No se encontró el bloque correspondiente.")


    if request.method == "POST":
        student_id = request.POST.get("student_id")
        status = request.POST.get("status")
        if student_id and status:
            student = get_object_or_404(Student, student_id=student_id)
            student.status = status
            student.save()

    # Aseguramos que todos los datos necesarios se envían al template
    students = block.students.all().order_by("-status", "name")
    return render(request, "schedules/students_in_block.html", {
        "tutor": tutor,
        "block": block,
        "block_id": block.block_id,
        "block_day": block.day,
        "block_number": block.block_number,
        "workshop": block.workshop,
        "students": students,
    })
