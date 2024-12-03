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
            if workshop.type == 'B':
                # Horarios para bachillerato
                create_blocks(workshop, high_school=True)
            elif workshop.type == 'P':
                # Horarios para primaria
                create_blocks(workshop, high_school=False)
            elif workshop.type == 'C':
                # Horarios para bachillerato y primaria (colectivas)
                create_blocks(workshop, high_school=True)
                create_blocks(workshop, high_school=False)

            return redirect('workshops:list_workshops')  # Cambia al nombre de tu vista/lista de talleres
    else:
        form = WorkshopForm()
    
    return render(request, 'workshops/create_workshop.html', {'form': form})

# Función para crear bloques
def create_blocks(workshop, high_school):
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    time_slots = [
        (time(8, 0), time(9, 0)),
        (time(9, 15), time(10, 15)),
        (time(10, 30), time(11, 30)),
    ]

    if high_school:
        time_slots += [(time(13, 0), time(14, 0))]  # Ejemplo de horario adicional para bachillerato
    
    for day in days:
        for start_time, end_time in time_slots:
            Block.objects.create(
                day=day,
                start_time=start_time,
                end_time=end_time,
                high_school=high_school,
                workshop=workshop
            )



