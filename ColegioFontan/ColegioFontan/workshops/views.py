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
            # Genera bloques según el tipo de taller
            if workshop.type == 'preschool':
                create_blocks(workshop, 'preschool')
            elif workshop.type == 'primary':
                create_blocks(workshop, 'primary')
            elif workshop.type == 'high_school':
                create_blocks(workshop, 'high_school')
            elif workshop.type == 'collective':
                # colectivos en preescolar, primaria y bachillerato
                for lvl in ('preschool','primary','high_school'):
                    create_blocks(workshop, lvl)
            messages.success(request, '¡El taller se ha creado correctamente con sus bloques!')
            return redirect('workshops:list_workshops')
    else:
        form = WorkshopForm()
    return render(request, 'workshops/create_workshop.html', {'form': form})


def create_blocks(workshop, block_type):
    """
    Crea bloques para todos los días incluyendo viernes con la misma cantidad
    para los niveles: 'preschool', 'primary', 'high_school'.
    Horarios de ejemplo que podrás ajustar luego.
    """
    def to_iso(hm):
        h, m = hm.split(':')
        return f"{int(h):02d}:{m}"

    schedules = {
        'preschool': [
            ("08:20","08:55"),
            ("10:00","10:50"),
            ("10:55","11:45"),
            ("13:30","14:30")
        ],
        'primary': [
            ("07:40","08:40"),
            ("09:10","10:20"),
            ("10:40","11:50"),
            ("12:30","13:30"),
            ("13:50","14:40")
        ],
        'high_school': [
            ("07:40","09:10"),
            ("09:40","11:00"),
            ("11:20","12:40"),
            ("13:20","14:40")
        ],
    }

    # Días de la semana
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Obtener los horarios para este tipo de bloque
    slots = schedules[block_type]
    
    # Crear bloques para todos los días con los mismos horarios
    for day in days:
        for idx, (start, end) in enumerate(slots, start=1):
            Block.objects.create(
                workshop=workshop,
                day=day,
                start_time=time.fromisoformat(to_iso(start)),
                end_time=time.fromisoformat(to_iso(end)),
                block_number=idx,
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
    old_type = workshop.type
    tutors   = Tutor.objects.all()

    form = WorkshopForm(request.POST or None, instance=workshop)

    if request.method == 'POST' and form.is_valid():
        w = form.save(commit=False)

        # Asignar tutor manualmente
        tutor_id = request.POST.get('tutor')
        w.tutor = Tutor.objects.filter(tutor_id=tutor_id).first() if tutor_id else None

        # Si el tipo es colectivo, asegurarse de que los campos auxiliares tengan valor
        if w.type == 'collective':
            # Solo asignar el valor principal si el campo está vacío o None
            if w.max_capacity_aux in [None, '']:
                w.max_capacity_aux = w.max_capacity
            if w.max_capacity_aux_preschool in [None, '']:
                w.max_capacity_aux_preschool = w.max_capacity

        w.save()

        new_type = w.type
        # Determinar los niveles requeridos según el tipo nuevo
        if new_type == 'collective':
            required_levels = ['preschool', 'primary', 'high_school']
        else:
            required_levels = [new_type]

        # Para cada nivel requerido, crear bloques solo si no existen
        for level in required_levels:
            if not Block.objects.filter(workshop=w, type=level).exists():
                create_blocks(w, level)

        messages.success(request, f"Taller «{w.name}» modificado correctamente.")
        return redirect('workshops:list_workshops')

    return render(request, 'workshops/modify_workshop.html', {
        'form': form,
        'tutors': tutors,
        'workshop': workshop,
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
    # Obtenemos los estudiantes ya ordenados
    students = Student.objects.filter(workshop=workshop)\
                              .order_by('-status', 'name')

    if request.method == "POST":
        # Recorremos cada estudiante y actualizamos su estado
        for student in students:
            key = f"status_{student.student_id}"
            new_status = request.POST.get(key)
            if new_status and student.status != new_status:
                student.status = new_status
                student.save()
        messages.success(request, "Estados actualizados correctamente.")
        return redirect('workshops:list_by_workshop', workshop_id=workshop_id)

    return render(request, "workshops/list_by_workshop.html", {
        "workshop": workshop,
        "students": students,
    })