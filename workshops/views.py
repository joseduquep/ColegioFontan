from django.shortcuts import render, redirect, get_object_or_404
from .forms import WorkshopForm
from .models import Workshop, Block
from datetime import time
from students.models import Student

def create_workshop(request):
    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        if form.is_valid():
            workshop = form.save()  # Guardamos el taller
            
            # Crear bloques según el tipo de taller
            if workshop.type == 'high_school':
                create_blocks(workshop, is_high_school=True)
            elif workshop.type == 'primary':
                create_blocks(workshop, is_high_school=False)
            elif workshop.type == 'collective':
                # Horarios para talleres colectivos (primaria y bachillerato)
                create_blocks(workshop, is_high_school=True)
                create_blocks(workshop, is_high_school=False)

            return redirect('workshops:list_workshops')  # Cambia según el nombre de tu vista/lista de talleres
    else:
        form = WorkshopForm()
    
    return render(request, 'workshops/create_workshop.html', {'form': form})


def create_blocks(workshop, is_high_school):
    """
    Crea bloques de horarios para un taller, incluyendo el número de bloque y el tipo.
    """
    def to_iso_time(hour_minute):
        if len(hour_minute.split(":")[0]) == 1:  # Si la hora tiene un solo dígito
            return f"0{hour_minute}"  # Agregar un cero inicial
        return hour_minute

    if is_high_school:
        schedules = {
            "Monday-Thursday": [
                ("7:40", "9:10"),  # 1
                ("9:40", "11:00"),  # 2
                ("11:20", "12:40"),  # 3
                ("13:20", "14:40"),  # 4
            ],
            "Friday": [
                ("7:40", "9:10"),  # 1
                ("9:50", "11:20"),  # 2
                ("11:50", "13:20"),  # 3
            ],
        }
        block_type = 'high_school'
    else:
        schedules = {
            "Monday-Thursday": [
                ("7:40", "8:40"),  # 1
                ("9:10", "10:20"),  # 2
                ("10:40", "11:50"),  # 3
                ("12:30", "13:30"),  # 4
                ("13:50", "14:40"),  # 5
            ],
            "Friday": [
                ("7:40", "8:40"),  # 1
                ("9:10", "10:20"),  # 2
                ("10:40", "11:50"),  # 3
                ("12:20", "13:20"),  # 4
            ],
        }
        block_type = 'primary'

    for day_group, time_slots in schedules.items():
        if day_group == "Monday-Thursday":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
        elif day_group == "Friday":
            days = ["Friday"]

        for day in days:
            for block_number, (start, end) in enumerate(time_slots, start=1):
                Block.objects.create(
                    workshop=workshop,
                    day=day,
                    start_time=time.fromisoformat(to_iso_time(start)),
                    end_time=time.fromisoformat(to_iso_time(end)),
                    block_number=block_number,  # Asignar el número de bloque
                    type=block_type  # Asignar el tipo de bloque
                )




def list_workshops(request):
    workshops = Workshop.objects.all()
    return render(request, 'workshops/list.html', {'workshops': workshops})


def students_by_workshop(request, workshop_id):
    # Obtén el taller específico usando el ID
    workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
    workshops = Workshop.objects.all()
    # Filtra los estudiantes que tienen asignado este taller
    students = Student.objects.filter(workshop=workshop)
    
    # Renderiza la plantilla con los datos
    return render(request, 'workshops/students_by_workshop.html', {
        'workshop': workshop,
        'students': students,
        'workshops': workshops,  # Lista de todos los talleres
    })


def show_blocks(request):
    blocks = Block.objects.all()
    blocks_with_students = []
    for block in blocks:
        students = block.students.all()
        blocks_with_students.append({'block': block, 'students': students})

    return render(request, 'workshops/show_blocks.html', {'blocks_with_students': blocks_with_students})
