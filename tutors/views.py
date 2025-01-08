from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from workshops.models import Workshop, Block
from tutors.models import Tutor
from schedules.models import Schedule


def show_tutors(request):
    workshops = Workshop.objects.all()
    query = request.GET.get('query', '')
    if query:
        tutors = Tutor.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    else:
        tutors = Tutor.objects.all()
    return render(request, 'tutors/show_tutors.html', {
        'workshops': workshops,
        'tutors': tutors,
        'query': query,
        'search_type': 'tutors'
    })


def tutor_schedule(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)

    schedule = {
        "Monday_Thursday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:30-1:30"],
        "Friday": ["7:40-8:40", "9:10-10:20", "10:40-11:50"],
    }
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Define el número de bloques para cada día
    blocks_per_day = {
        "Monday": 4,
        "Tuesday": 4,
        "Wednesday": 4,
        "Thursday": 4,
        "Friday": 3,
    }

    # Generar horario de Bachillerato
    tutor_schedules = Schedule.objects.filter(block__workshop__tutor=tutor).select_related('block', 'block__workshop')
    tutor_schedule_table = []
    for block_number in range(1, 5):  # Solo hasta 4 bloques para Bachillerato
        row = []
        for day in days_of_week:
            if block_number > blocks_per_day[day]:
                row.append({"day": day, "block_number": None, "workshop": None})
            else:
                workshop_name = next(
                    (entry.block.workshop.name for entry in tutor_schedules
                     if entry.block.block_number == block_number and entry.block.day == day),
                    None
                )
                row.append({
                    "day": day,
                    "block_number": block_number,
                    "workshop": workshop_name,
                })
        tutor_schedule_table.append(row)

    # Generar horario de Primaria
    primary_workshops = tutor.workshops.filter(type='primary')
    primary_schedule = Block.objects.filter(workshop__in=primary_workshops)
    primary_schedule_table = []
    for block_number in range(1, 6):  # Hasta 5 bloques para Primaria
        row = []
        for day in days_of_week:
            if (day == "Friday" and block_number > 4) or (day != "Friday" and block_number > 5):
                row.append({"day": day, "block_number": None, "workshop": None})
            else:
                workshop_name = next(
                    (block.workshop.name for block in primary_schedule
                     if block.block_number == block_number and block.day == day),
                    None
                )
                row.append({
                    "day": day,
                    "block_number": block_number,
                    "workshop": workshop_name,
                })
        primary_schedule_table.append(row)

    context = {
        "tutor": tutor,
        "tutor_id": tutor_id,
        "tutor_schedule_table": tutor_schedule_table,
        "days_of_week": days_of_week,
        "primary_schedule_table": primary_schedule_table,
    }

    return render(request, "schedules/tutor_schedule.html", context)
