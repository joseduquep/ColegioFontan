from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import WorkshopForm
from .models import Workshop, Block
from datetime import time
from students.models import Student
from django.contrib import messages
from tutors.models import Tutor
from django.contrib.auth.decorators import login_required

@login_required
def create_workshop(request):
    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        if form.is_valid():
            workshop = form.save()
            if workshop.type == 'high_school':
                create_blocks(workshop, is_high_school=True)
            elif workshop.type == 'primary':
                create_blocks(workshop, is_high_school=False)
            elif workshop.type == 'collective':
                create_blocks(workshop, is_high_school=True)
                create_blocks(workshop, is_high_school=False)
            messages.success(request, '¡El taller se ha creado correctamente!')
            return redirect('workshops:list_workshops')
        
    else:
        form = WorkshopForm()
    return render(request, 'workshops/create_workshop.html', {'form': form})

@login_required
def create_blocks(workshop, is_high_school):
    def to_iso_time(hour_minute):
        return f"0{hour_minute}" if len(hour_minute.split(":")[0]) == 1 else hour_minute

    schedules = {
        "high_school": {
            "Monday-Thursday": [("7:40", "9:10"), ("9:40", "11:00"), ("11:20", "12:40"), ("13:20", "14:40")],
            "Friday": [("7:40", "9:10"), ("9:50", "11:20"), ("11:50", "13:20")]
        },
        "primary": {
            "Monday-Thursday": [("7:40", "8:40"), ("9:10", "10:20"), ("10:40", "11:50"), ("12:30", "13:30"), ("13:50", "14:40")],
            "Friday": [("7:40", "8:40"), ("9:10", "10:20"), ("10:40", "11:50"), ("12:20", "13:20")]
        }
    }

    block_type = 'high_school' if is_high_school else 'primary'
    schedule = schedules[block_type]

    for day_group, time_slots in schedule.items():
        days = ["Monday", "Tuesday", "Wednesday", "Thursday"] if day_group == "Monday-Thursday" else ["Friday"]
        for day in days:
            for block_number, (start, end) in enumerate(time_slots, start=1):
                Block.objects.create(
                    workshop=workshop,
                    day=day,
                    start_time=time.fromisoformat(to_iso_time(start)),
                    end_time=time.fromisoformat(to_iso_time(end)),
                    block_number=block_number,
                    type=block_type
                )

@login_required
def list_workshops(request):
    workshops = Workshop.objects.all()
    return render(request, 'workshops/workshops_list.html', {'workshops': workshops})

@login_required
def students_by_workshop(request, workshop_id):
    print("cargando funcion de estudiantes por taller")
    workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
    print("cargando funcion de estudiantes por taller")
    students = Student.objects.filter(workshop=workshop)
    return render(request, 'workshops/students_by_workshop.html', {
        'workshop': workshop,
        'students': students,
        'workshops': Workshop.objects.all()
    })


from django.core.paginator import Paginator
@login_required
def show_blocks(request):
    blocks_with_students = [
        {'block': block, 'students': block.students.all()}
        for block in Block.objects.all()
    ]
    paginator = Paginator(blocks_with_students, 50)  # 10 bloques por página
    page_number = request.GET.get('page')  # Página actual
    page_obj = paginator.get_page(page_number)

    return render(request, 'workshops/show_blocks.html', {
        'blocks_with_students': page_obj,  # Pasamos solo la página actual
    })


@login_required
def modify_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
    tutors = Tutor.objects.all()  # Listar todos los tutores disponibles

    if request.method == 'POST':
        # Actualizar los datos del taller
        workshop.name = request.POST.get('name', workshop.name)
        workshop.type = request.POST.get('type', workshop.type)
        workshop.max_capacity = request.POST.get('max_capacity', workshop.max_capacity)
        
        # Asignar tutor al taller (si se selecciona)
        tutor_id = request.POST.get('tutor')
        if tutor_id:
            workshop.tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
        else:
            workshop.tutor = None  # Eliminar tutor asignado si no se selecciona ninguno

        workshop.save()
        messages.success(request, f"{workshop.name} modificado exitosamente.")
        return redirect('workshops:list_workshops')

    return render(request, 'workshops/modify_workshop.html', {
        'workshop': workshop,
        'tutors': tutors,
    })

@login_required
def confirm_delete_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
    return render(request, 'workshops/confirm_delete_workshop.html', {'workshop': workshop})

@login_required
def delete_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
    if request.method == 'POST':
        workshop.delete()
        messages.success(request, f"{workshop.name} eliminado exitosamente.")
        return redirect('workshops:list_workshops')
    return redirect('workshops:modify_workshop', workshop_id=workshop_id)

@login_required
def list_by_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, workshop_id=workshop_id)

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        status = request.POST.get("status")
        if student_id and status:
            student = get_object_or_404(Student, student_id=student_id)
            student.status = status
            student.save()

    # Filtrar estudiantes que pertenecen a este taller
    students = Student.objects.filter(workshop=workshop).order_by("-status", "name")
    return render(request, "workshops/list_by_workshop.html", {
        "workshop": workshop,
        "students": students,
    })