from django.shortcuts import render, redirect, get_object_or_404
from .models import Schedule
from students.models import Student
from datetime import time
from .models import Schedule
from workshops.models import Block
from students.models import Student
from workshops.models import Workshop
from django.http import HttpResponseRedirect


def schedule_index(request):
    # Obtener todos los estudiantes para mostrar en la página de horarios
    students = Student.objects.all()
    
    # Depuración: Imprimir los estudiantes para ver si tienen un ID válido
    print(students)  # Esto imprimirá en la consola de Django
    
    return render(request, 'schedules/schedule_index.html', {'students': students})


# Definir las horas y los días (ajusta según tus necesidades)
hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def default_schedule():
    """
    Esta función genera un horario por defecto con algunos bloques de ejemplo.
    """
    blocks = {
        'Monday': [
            {'start_time': '08:00', 'end_time': '09:00', 'workshop': 'Math'},
            {'start_time': '10:00', 'end_time': '11:00', 'workshop': 'English'},
        ],
        'Tuesday': [
            {'start_time': '09:00', 'end_time': '10:00', 'workshop': 'Science'},
        ],
        'Wednesday': [
            {'start_time': '08:00', 'end_time': '09:00', 'workshop': 'History'},
            {'start_time': '11:00', 'end_time': '12:00', 'workshop': 'Art'},
        ],
        'Thursday': [
            {'start_time': '10:00', 'end_time': '11:00', 'workshop': 'Geography'},
        ],
        'Friday': [
            {'start_time': '13:00', 'end_time': '14:00', 'workshop': 'Computer Science'},
        ]
    }
    return blocks



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
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        day = request.POST.get('day')
        block = request.POST.get('block')
        workshop_id = request.POST.get('workshop')
        
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
        
        # Crear o actualizar la entrada del horario con el taller seleccionado
        schedule_entry, created = Schedule.objects.get_or_create(
            student=student,
            day=day,
            block=block,
            defaults={'workshop': workshop}
        )
        
        # Redirigir de nuevo al horario del estudiante después de agregar el taller
        return redirect('student_schedule', student_id=student.student_id)

    # Redirigir al horario del estudiante si no es una solicitud POST
    return redirect('student_schedule', student_id=student.student_id)






































def update_schedule(request, student_id):
    student = Student.objects.get(pk=student_id)

    if request.method == 'POST':
        # Obtener los datos del formulario
        day = request.POST['day']
        time = request.POST['time']
        workshop_id = request.POST['workshop']
        
        # Obtener el workshop seleccionado
        workshop = Workshop.objects.get(pk=workshop_id)
        
        # Crear un nuevo bloque
        block = Block.objects.create(
            student=student,
            day=day,
            start_time=time,
            end_time=calculate_end_time(time),  # Función para calcular la hora de fin
            workshop=workshop
        )
        
        # Crear el schedule que asocia el estudiante con el bloque
        Schedule.objects.create(student=student, block=block)
        
        # Redirigir al usuario a la página del horario
        return redirect('student_schedule', student_id=student.id)

    else:
        # Si no es un POST, mostramos el formulario para personalizar el horario
        workshops = Workshop.objects.all()
        return render(request, 'schedule/update_schedule.html', {'student': student, 'workshops': workshops})

def calculate_end_time(start_time):
    # Aquí puedes definir una duración fija para todos los bloques, como 1 hora
    from datetime import datetime, timedelta
    start_time_obj = datetime.strptime(str(start_time), '%H:%M')
    end_time_obj = start_time_obj + timedelta(hours=1)
    return end_time_obj.time()


