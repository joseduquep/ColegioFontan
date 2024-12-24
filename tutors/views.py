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
        "Monday_Thursday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:30-1:30", "1:50-2:40"],
        "Friday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:20-1:20"],
    }
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    num_blocks = range(1, len(schedule["Monday_Thursday"]) + 1)

    tutor_schedules = Schedule.objects.filter(block__workshop__tutor=tutor).select_related('block', 'block__workshop')

    tutor_schedule_table = []
    for block_number in num_blocks:
        row = []
        for day in days_of_week:
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

    context = {
        "tutor": tutor,
        "tutor_schedule_table": tutor_schedule_table,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
    }

    return render(request, "schedules/tutor_schedule.html", context)
