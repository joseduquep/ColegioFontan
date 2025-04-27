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
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib import messages
from django.db.models import Count


# Configuración básica de logging
logger = logging.getLogger(__name__)



# Función auxiliar: Determinar horario y talleres disponibles
def get_schedule_and_workshops(student):
    """
    Devuelve (bloques, talleres) filtrados según grado y colectivos,
    incluyendo Preescolar cuando student.grade == 0.
    """
    if student.grade == 0:
        tipos = ['preschool', 'collective']
    elif student.grade > 5:
        tipos = ['high_school', 'collective']
    else:
        tipos = ['primary', 'collective']

    bloques = (
        Block.objects
             .filter(workshop__type__in=tipos)
             .select_related('workshop')
             .annotate(student_count=Count('students'))
    )

    talleres = Workshop.objects.filter(type__in=tipos)

    return bloques, list(talleres)


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

    # Definir bloques según el grado
    if student.grade > 5 or student.grade < 1:
        blocks_per_day = {
            "Monday": 4,
            "Tuesday": 4,
            "Wednesday": 4,
            "Thursday": 4,
            "Friday": 3,
        }
    else:
        blocks_per_day = {
            "Monday": 5,
            "Tuesday": 5,
            "Wednesday": 5,
            "Thursday": 5,
            "Friday": 4,
        }

    num_blocks = range(1, max(blocks_per_day.values()) + 1)

    # Generar la tabla del horario
    student_schedule = Schedule.objects.filter(student=student).select_related('block')
    schedule_table = [
        [
            {
                "day": day,
                "block_number": block_number if block_number <= blocks_per_day[day] else None,
                "workshop": next(
                    (entry.block.workshop for entry in student_schedule
                     if entry.block.block_number == block_number and entry.block.day == day),
                    None
                ) if block_number <= blocks_per_day[day] else None,
                "tutor": next(
                    (entry.block.workshop.tutor.user.get_full_name() for entry in student_schedule
                     if entry.block.block_number == block_number and entry.block.day == day and entry.block.workshop.tutor),
                    None
                ) if block_number <= blocks_per_day[day] else None,
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




# schedules/utils.py


def get_block_capacity(workshops, day, block_number, block_type):
    """
    Agrega a cada workshop un atributo .current_capacity
    con el número de estudiantes asignados a ese bloque.
    """
    for w in workshops:
        # buscamos el bloque concreto para este workshop, día y número
        block = Block.objects.filter(
           workshop=w,
           day=day,
           block_number=block_number,
           type=block_type
       ).first()
        # si existe, contamos los estudiantes en ese bloque; si no, 0
        w.current_capacity = block.students.count() if block else 0


@login_required
def select_workshop(request, student_id, day, block_number):
    student = get_object_or_404(Student, student_id=student_id)
    _, workshops = get_schedule_and_workshops(student)
    
    block_type = request.GET.get('type')
    if block_type not in ('primary', 'high_school', 'preschool'):
        if student.grade == 0:
            block_type = 'preschool'
        elif student.grade > 5:
            block_type = 'high_school'
        else:
            block_type = 'primary'
    get_block_capacity(workshops, day, block_number, block_type)
    # 1) Primero sacamos el tipo de bloque del parámetro ?type=… (viene de los enlaces)
    block_type = request.GET.get('type')
    if block_type not in ('primary', 'high_school', 'preschool'):
        if student.grade == 0:
            block_type = 'preschool'
        elif student.grade > 5:
            block_type = 'high_school'
        else:
            block_type = 'primary'

    if request.method == "POST":
        # nos aseguramos de recibirlo también en el form
        block_type = request.POST.get('type', block_type)

        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)

        # filtramos blocks POR TIPO también
        block = Block.objects.filter(
            block_number=block_number,
            day=day,
            workshop=workshop,
            type=block_type
        ).first()

        # calculamos capacidad
        if workshop.type == 'collective':
            if block_type == 'preschool' and workshop.max_capacity_aux_preschool:
                capacity = workshop.max_capacity_aux_preschool
            elif block_type == 'high_school' and workshop.max_capacity_aux:
                capacity = workshop.max_capacity_aux
            else:
                capacity = workshop.max_capacity
        else:
            capacity = workshop.max_capacity

        if not block or block.students.count() >= capacity:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'student_id': student_id,
                'workshops': workshops,
                'day': day,
                'block_number': block_number,
                'block_type': block_type,
                'error': f'Capacidad máxima ({capacity}) o bloque no existe.',
            })

    
        old_blocks = Block.objects.filter(
            students=student,
            day=day,
            block_number=block_number
        )
        for ob in old_blocks:
            ob.students.remove(student)
        
        Schedule.objects.filter(
            student=student,
            block__day=day,
            block__block_number=block_number
        ).delete()
        # ——————————————————————————————

        # creamos la nueva asignación
        Schedule.objects.create(student=student, block=block)
        block.students.add(student)

        return HttpResponseRedirect(reverse('student_schedule', args=[student_id]))

    # GET: enviamos block_type al template
    return render(request, 'schedules/select_workshop.html', {
        'student': student,
        'student_id': student_id,
        'workshops': workshops,
        'day': day,
        'block_number': block_number,
        'block_type': block_type,
    })



def select_block(request, tutor_id, day, block_number):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    blocks = Block.objects.filter(day=day, block_number=block_number)

    return render(request, 'schedules/students_by_block.html', {
        'tutor': tutor,
        'blocks': blocks,
        'day': day,
        'block_number': block_number,
    })



def students_in_block(request, tutor_id, day, block_number):
    block_type = request.GET.get("type")
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    block = Block.objects.filter(
        day=day,
        block_number=block_number,
        type=block_type,
        workshop__tutor=tutor
    ).first()
    if not block:
        raise Http404("Bloque no encontrado")

    if request.method == "POST":
        # Recorremos cada estudiante del bloque y actualizamos su estado
        for student in block.students.all():
            key = f"status_{student.student_id}"
            new_status = request.POST.get(key)
            if new_status and student.status != new_status:
                student.status = new_status
                student.save()
        messages.success(request, "Estados actualizados correctamente")
        return redirect(request.path + f"?type={block_type}")

    students = block.students.all().order_by("-status", "name")
    return render(request, "schedules/students_in_block.html", {
        "tutor": tutor,
        "tutor_id": tutor.tutor_id,
        "block": block,
        "block_number": block.block_number,
        "block_day": block.day,
        "workshop": block.workshop,
        "students": students,
    })



@login_required
def delete_workshop(request, student_id, day, block_number):
    if request.method != 'POST':
        return redirect('student_schedule', student_id)

    student = get_object_or_404(Student, student_id=student_id)

    # Borra registros intermedios
    Schedule.objects.filter(
        student=student,
        block__day=day,
        block__block_number=block_number
    ).delete()

    # Quita la relación M2M de Block.students de forma segura
    block = Block.objects.filter(
        students=student,
        day=day,
        block_number=block_number
    ).first()
    if block:
        block.students.remove(student)

    messages.success(request, "Taller eliminado correctamente.")
    return redirect('student_schedule', student_id)
