from django.shortcuts import render, redirect, get_object_or_404
from .models import Schedule
from students.models import Student
from .models import Schedule
from workshops.models import Block
from students.models import Student
from workshops.models import Workshop
from django.http import HttpResponseRedirect
from django.http import JsonResponse



def student_schedule(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    is_high_school = student.grade > 5

    # Definimos el horario según el grado
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

    # Lista de días y bloques
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    num_blocks = range(1, len(schedule["Monday_Thursday"]) + 1)  # 1 a 4 si es primaria, 1 a 5 si es secundaria
    friday_blocks = len(schedule["Friday"])  # Para mostrar solo los bloques disponibles del viernes

    # Verificar si se presionó un botón de "Agregar Taller"
    selected_block = None
    if request.method == 'POST':
        selected_block = request.POST.get('selected_block')
        talleres = Workshop.objects.all()  # Cambia esto si necesitas filtrar los talleres por primaria/secundaria

        # Si se seleccionó un taller, guardar la selección y redirigir
        if 'taller' in request.POST:
            taller_id = request.POST.get('taller')
            taller = get_object_or_404(Workshop, id=taller_id)

            # Aquí deberías guardar la relación entre el estudiante, el bloque y el taller
            # Por ejemplo, si tienes un modelo de inscripción de talleres, guardarlo aquí

            return HttpResponseRedirect(request.path)

    context = {
        "student": student,
        "schedule": schedule,
        "is_high_school": is_high_school,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
        "selected_block": selected_block,
        "friday_blocks": friday_blocks,
        "workshops": workshops,
    }

    return render(request, "schedules/schedule.html", context)



def add_workshop(request, student_id):
    if request.method == 'POST':

        student = get_object_or_404(Student, student_id=student_id)
        

        block_number = request.POST.get('block')
        day = request.POST.get('day')
        workshop_id = request.POST.get('workshop')
        

        block_number = int(block_number)
        workshop_id = int(workshop_id)
            

        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
            

        blocks_for_day_and_workshop = Block.objects.filter(day=day, workshop=workshop).order_by('start_time')
            

            

        block = blocks_for_day_and_workshop[block_number - 1]
        print(f"block_id recibido: {block.block_id}")


        if Schedule.objects.filter(student=student, block=block).exists():
            return JsonResponse({'error': "Ya has agregado este bloque."}, status=400)
            

        current_capacity = Schedule.objects.filter(block=block).count()
        if current_capacity >= workshop.max_capacity:
            return JsonResponse({'error': "El taller seleccionado ha alcanzado su capacidad máxima."}, status=400)

        Schedule.objects.create(
            student=student,
            block=block,
            high_school=student.grade > 5
        )
            
        return JsonResponse({'workshop_name': workshop.name})
        

        
    # Si no es una solicitud POST válida
    return JsonResponse({'error': 'Solicitud inválida.'}, status=400)

















