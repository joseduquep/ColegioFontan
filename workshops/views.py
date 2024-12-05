from django.shortcuts import render, redirect
from .forms import WorkshopForm
from .models import Workshop, Block
from datetime import time

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
    Crea bloques de horarios para un taller.
    """
    if is_high_school:
        schedules = {
            "Monday-Thursday": [
                ("7:40", "9:10"),
                ("9:40", "11:00"),
                ("11:20", "12:40"),
                ("13:20", "14:40"),
            ],
            "Friday": [
                ("7:40", "9:10"),
                ("9:50", "11:20"),
                ("11:50", "13:20"),
            ],
        }
    else:
        schedules = {
            "Monday-Thursday": [
                ("7:40", "8:40"),
                ("9:10", "10:20"),
                ("10:40", "11:50"),
                ("12:30", "13:30"),
                ("13:50", "14:40"),
            ],
            "Friday": [
                ("7:40", "8:40"),
                ("9:10", "10:20"),
                ("10:40", "11:50"),
                ("12:20", "13:20"),
            ],
        }

    # Convertir las horas a formato ISO válido
    def to_iso_time(hour_minute):
        if len(hour_minute.split(":")[0]) == 1:  # Si la hora tiene un solo dígito
            return f"0{hour_minute}"  # Agregar un cero inicial
        return hour_minute

    for day_group, time_slots in schedules.items():
        if day_group == "Monday-Thursday":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
        elif day_group == "Friday":
            days = ["Friday"]

        for day in days:
            for start, end in time_slots:
                Block.objects.create(
                    workshop=workshop,
                    day=day,
                    start_time=time.fromisoformat(to_iso_time(start)),
                    end_time=time.fromisoformat(to_iso_time(end)),
                )


def list_workshops(request):
    workshops = Workshop.objects.all()
    return render(request, 'workshops/list.html', {'workshops': workshops})


