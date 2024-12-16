# views.py

from django.shortcuts import render, get_object_or_404
from workshops.models import Workshop
from .models import Tutor
from django.db.models import Q  # Importar Q para consultas complejas
from tutors.models import Tutor
from workshops.models import Workshop, Block
from schedules.models import Schedule

# Vista para mostrar los tutores y los workshops
def show_tutors(request):
    workshops = Workshop.objects.all()  # Obtener todos los workshops
    query = request.GET.get('query', '')  # Obtener la consulta de búsqueda
    if query:
        # Filtrar por username, first_name o last_name
        tutors = Tutor.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    else:
        tutors = Tutor.objects.all()  # Obtener todos los tutores
    return render(request, 'tutors/show_tutors.html', {'workshops': workshops, 'tutors': tutors, 'query': query, 'search_type': 'tutors'})

# Vista para mostrar el horario del tutor


def tutor_schedule(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)

    # Ejemplo de horario similar al del estudiante. Ajusta según tus necesidades.
    # Aquí asumimos que los tutores utilizan la misma lógica de bloques que los estudiantes.
    # Si el tutor no depende de primaria/secundaria, podrías usar directamente el horario extendido.
    schedule = {
        "Monday_Thursday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:30-1:30", "1:50-2:40"],
        "Friday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:20-1:20"],
    }

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    # Determinamos el número de bloques según el mayor número de bloques en Monday_Thursday
    num_blocks = range(1, len(schedule["Monday_Thursday"]) + 1)

    # Filtrar los Schedules asociados a los bloques de los workshops de este tutor
    # Asumiendo que Workshop tiene un campo tutor: workshop.tutor = tutor
    tutor_schedules = Schedule.objects.filter(block__workshop__tutor=tutor).select_related('block', 'block__workshop')

    # Construir la tabla del horario
    tutor_schedule_table = []
    for block_number in num_blocks:
        row = []
        for day in days_of_week:
            workshop_name = None
            for entry in tutor_schedules:
                if entry.block.block_number == block_number and entry.block.day == day:
                    workshop_name = entry.block.workshop.name
                    break
            row.append({
                "day": day,
                "block_number": block_number,
                "workshop": workshop_name,
            })
        tutor_schedule_table.append(row)

    context = {
        "tutor": tutor,
        "tutor_schedule_table": tutor_schedule_table,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
    }

    return render(request, "schedules/tutor_schedule.html", context)

