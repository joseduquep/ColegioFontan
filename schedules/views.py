from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
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
    friday_blocks = len(schedule["Friday"])

    # Recuperar horarios del estudiante
    student_schedule = Schedule.objects.filter(student=student).select_related('block', 'block__workshop')

    # Organizar datos en una estructura amigable para plantillas
    schedule_table = []
    for block in num_blocks:
        row = []
        for day in days_of_week:
            workshop_name = None
            for entry in student_schedule:
                if entry.block.block_id == block and entry.block.day == day:
                    workshop_name = entry.block.workshop.name
                    break
            row.append({"day": day, "block": block, "workshop": workshop_name})
        schedule_table.append(row)

    context = {
        "student": student,
        "schedule_table": schedule_table,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
        "friday_blocks": friday_blocks,
        "workshops": workshops,
    }

    return render(request, "schedules/schedule.html", context)

def select_workshop(request, student_id, day, block):
    student = get_object_or_404(Student, student_id=student_id)
    
    # Determinar qué tipo de talleres mostrar basado en el grado del estudiante
    is_high_school = student.grade > 5
    if is_high_school:
        workshops = Workshop.objects.filter(type__in=['high_school', 'collective'])
    else:
        workshops = Workshop.objects.filter(type__in=['primary', 'collective'])

    if request.method == "POST":
        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
        
        # Recuperar el bloque correspondiente
        block_obj = get_object_or_404(Block, block_id=block, day=day)

        # Verificar si el estudiante ya tiene un taller en este bloque
        if Schedule.objects.filter(student=student, block=block_obj).exists():
            return render(request, 'select_workshop.html', {
                'student': student,
                'workshops': workshops,
                'day': day,
                'block': block,
                'error': 'Ya tienes un taller asignado en este bloque.'
            })

        # Verificar capacidad del taller
        current_capacity = Schedule.objects.filter(block=block_obj).count()
        if current_capacity >= workshop.max_capacity:
            return render(request, 'select_workshop.html', {
                'student': student,
                'workshops': workshops,
                'day': day,
                'block': block,
                'error': 'El taller seleccionado ha alcanzado su capacidad máxima.'
            })

        # Crear la programación del taller
        Schedule.objects.create(
            student=student,
            block=block_obj,
            workshop=workshop
        )

        # Redirigir de vuelta al horario del estudiante
        return HttpResponseRedirect(reverse('student_schedule', args=[student_id]))

    return render(request, 'select_workshop.html', {
        'student': student,
        'workshops': workshops,
        'day': day,
        'block': block,
    })

def add_workshop(request, student_id):
    # This method can be removed or kept as a legacy method if needed
    # It seems redundant with the new select_workshop view
    if request.method == 'POST':
        student = get_object_or_404(Student, student_id=student_id)
        block_id = int(request.POST.get('block'))
        day = request.POST.get('day')
        workshop_id = int(request.POST.get('workshop'))

        try:
            # Recuperar el bloque correspondiente
            block = get_object_or_404(Block, block_id=block_id, day=day)

            # Verificar existencia del taller
            if Schedule.objects.filter(student=student, block=block).exists():
                return JsonResponse({'error': "Ya has agregado este bloque."}, status=400)

            # Verificar capacidad máxima
            workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
            current_capacity = Schedule.objects.filter(block=block).count()
            if current_capacity >= workshop.max_capacity:
                return JsonResponse({'error': "El taller seleccionado ha alcanzado su capacidad máxima."}, status=400)

            # Crear el horario
            schedule = Schedule.objects.create(
                student=student,
                block=block,
                workshop=workshop
            )
            return JsonResponse({'workshop_name': workshop.name, 'block': block_id, 'day': day})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Solicitud inválida.'}, status=400)







def select_workshop(request, student_id, day, block):
    student = get_object_or_404(Student, student_id=student_id)
    
    # Explicitly convert block to an integer
    block_number = int(block)
    
    # Debug prints
    print(f"Student: {student.name}")
    print(f"Day: {day}")
    print(f"Block: {block}")
    print(f"Block Type: {type(block)}")

    # Determinar qué tipo de talleres mostrar basado en el grado del estudiante
    is_high_school = student.grade > 5
    if is_high_school:
        workshops = Workshop.objects.filter(type__in=['high_school', 'collective'])
    else:
        workshops = Workshop.objects.filter(type__in=['primary', 'collective'])

    context = {
        'student': student,
        'workshops': workshops,
        'day': day,
        'block_number': block_number,  # Ensure this is a simple integer
    }

    if request.method == "POST":
        print("entre al post")
        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
        
        # Recuperar el bloque correspondiente
        block_obj = get_object_or_404(Block, block_id=block, day=day)

        # Rest of the existing logic...
    return render(request, 'schedules/select_workshop.html', context)