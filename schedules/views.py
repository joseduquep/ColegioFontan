from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Schedule
from students.models import Student
from workshops.models import Block, Workshop

def student_schedule(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    is_high_school = student.grade > 5

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

    student_schedule = Schedule.objects.filter(student=student).select_related('block')

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


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Schedule
from students.models import Student
from workshops.models import Block, Workshop

def select_workshop(request, student_id, day, block_number):
    student = get_object_or_404(Student, student_id=student_id)

    is_high_school = student.grade > 5
    if is_high_school:
        workshops = Workshop.objects.filter(type__in=['high_school', 'collective'])
    else:
        workshops = Workshop.objects.filter(type__in=['primary', 'collective'])

    # Agregar atributo actual a cada workshop
    for w in workshops:
        block_obj = Block.objects.filter(workshop=w, day=day, block_number=block_number).first()
        if block_obj:
            current_capacity = block_obj.students.count()
            w.current_capacity = current_capacity
        else:
            w.current_capacity = 0

    if request.method == "POST":
        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)

        block_obj = Block.objects.filter(
            block_number=block_number,
            day=day,
            workshop=workshop
        ).first()

        if not block_obj:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'workshops': workshops,
                'day': day,
                'block': block_number,
                'error': 'Bloque no encontrado.',
            })

        current_capacity = block_obj.students.count()
        if current_capacity >= workshop.max_capacity:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'workshops': workshops,
                'day': day,
                'block': block_number,
                'error': 'El taller seleccionado ha alcanzado su capacidad máxima.',
            })

        # Eliminar cualquier asignación previa del mismo bloque y día para este estudiante
        existing_schedules = Schedule.objects.filter(student=student, block__day=day, block__block_number=block_number)
        for sch in existing_schedules:
            sch.block.students.remove(student)
            sch.delete()

        # Crear la nueva programación
        schedule_entry = Schedule.objects.create(
            student=student,
            block=block_obj
        )
        block_obj.students.add(student)

        return HttpResponseRedirect(reverse('student_schedule', args=[student_id]))

    return render(request, 'schedules/select_workshop.html', {
        'student': student,
        'workshops': workshops,
        'day': day,
        'block': block_number,
    })

