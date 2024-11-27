from django.shortcuts import render
from .models import Schedule
from students.models import Student
from datetime import time


from django.shortcuts import render
from students.models import Student

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
    # Aquí usaríamos default_schedule() para obtener un horario estático por defecto.
    blocks = default_schedule()

    # Pasar los bloques al template de forma estructurada por días y horas
    # Vamos a estructurarlo de forma más accesible para el template
    days_schedule = {
        day: blocks[day] for day in days
    }

    context = {
        'days_schedule': days_schedule,
        'hours': hours,
        'days': days
    }

    return render(request, 'schedules/student_schedule.html', context)


from django.shortcuts import render, redirect
from .models import Schedule
from workshops.models import Block
from students.models import Student
from workshops.models import Workshop

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
