from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Schedule
from students.models import Student
from workshops.models import Block, Workshop
from django.contrib.auth.decorators import login_required
from tutors.models import Tutor

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

    student_schedule = Schedule.objects.filter(student=student).select_related('block')

    schedule_table = []
    for block_number in num_blocks:
        row = []
        for day in days_of_week:
            workshop_name = None
            for entry in student_schedule:
                if entry.block.block_number == block_number and entry.block.day == day:
                    workshop_name = entry.block.workshop.name
                    break
            row.append({
                "day": day,
                "block_number": block_number,
                "workshop": workshop_name,
            })
        schedule_table.append(row)

    context = {
        "student": student,
        "schedule_table": schedule_table,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
        "workshops": workshops,
    }

    return render(request, "schedules/schedule.html", context)


def select_workshop(request, student_id, day, block_number):
    student = get_object_or_404(Student, student_id=student_id)
    is_high_school = student.grade > 5
    workshops = Workshop.objects.filter(type__in=['high_school', 'collective']) if is_high_school else Workshop.objects.filter(type__in=['primary', 'collective'])

    for workshop in workshops:
        block_obj = Block.objects.filter(workshop=workshop, day=day, block_number=block_number).first()
        workshop.current_capacity = block_obj.students.count() if block_obj else 0

    if request.method == "POST":
        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)

        block_obj = Block.objects.filter(block_number=block_number, day=day, workshop=workshop).first()

        if not block_obj:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'workshops': workshops,
                'day': day,
                'block': block_number,
                'error': 'Bloque no encontrado.',
            })

        if block_obj.students.count() >= workshop.max_capacity:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'workshops': workshops,
                'day': day,
                'block': block_number,
                'error': 'El taller seleccionado ha alcanzado su capacidad máxima.',
            })

        existing_schedules = Schedule.objects.filter(student=student, block__day=day, block__block_number=block_number)
        for schedule in existing_schedules:
            schedule.block.students.remove(student)
            schedule.delete()

        schedule_entry = Schedule.objects.create(student=student, block=block_obj)
        block_obj.students.add(student)

        return HttpResponseRedirect(reverse('student_schedule', args=[student_id]))

    return render(request, 'schedules/select_workshop.html', {
        'student': student,
        'workshops': workshops,
        'day': day,
        'block': block_number,
    })


@login_required
def select_block(request, tutor_id, day, block_number):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)

    blocks = Block.objects.filter(day=day, block_number=block_number)

    for b in blocks:
        b.current_capacity = b.students.count()

    if request.method == "POST":
        block_id = request.POST.get('block_id')
        block_obj = get_object_or_404(Block, block_id=block_id, day=day, block_number=block_number)

        current_capacity = block_obj.students.count()
        if current_capacity >= block_obj.workshop.max_capacity:
            return render(request, 'schedules/select_block.html', {
                'tutor': tutor,
                'blocks': blocks,
                'day': day,
                'block_number': block_number,
                'error': 'El bloque seleccionado ha alcanzado su capacidad máxima.',
            })

        existing_schedules = Schedule.objects.filter(tutor=tutor, block__day=day, block__block_number=block_number)
        for sch in existing_schedules:
            sch.block.students.remove(*sch.block.students.all())
            sch.delete()

        schedule_entry = Schedule.objects.create(tutor=tutor, block=block_obj)

        return HttpResponseRedirect(reverse('tutor_schedule', args=[tutor_id]))

    return render(request, 'schedules/select_block.html', {
        'tutor': tutor,
        'blocks': blocks,
        'day': day,
        'block_number': block_number,
    })
