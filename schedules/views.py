from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Schedule
from students.models import Student
from workshops.models import Block, Workshop
from tutors.models import Tutor
import logging
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.contrib import messages
from django.db.models import Count, Q
from django.db import transaction
from django.views.decorators.http import require_POST


# Configuración básica de logging
logger = logging.getLogger(__name__)



# Funciones auxiliares de niveles y horarios
def get_student_level_types(student):
    """
    Retorna los tipos de nivel académico habilitados para el estudiante.
    Regla especial: grado 5 es mixto (primary + high_school).
    """
    if student.grade <= 0:
        return ['preschool']
    if student.grade == 5:
        return ['primary', 'high_school']
    if student.grade > 5:
        return ['high_school']
    return ['primary']


def get_blocks_per_level(level_type):
    return 4 if level_type in ('high_school', 'preschool') else 5


def build_level_schedule_table(student_schedule, days_of_week, level_type):
    num_blocks = range(1, get_blocks_per_level(level_type) + 1)
    schedule_table = [
        [
            {
                "day": day,
                "block_number": block_number,
                "block_type": level_type,
                "workshop": next(
                    (
                        entry.block.workshop
                        for entry in student_schedule
                        if entry.block.type == level_type
                        and entry.block.block_number == block_number
                        and entry.block.day == day
                    ),
                    None
                ),
                "tutor": next(
                    (
                        entry.block.workshop.tutor.user.get_full_name()
                        for entry in student_schedule
                        if entry.block.type == level_type
                        and entry.block.block_number == block_number
                        and entry.block.day == day
                        and entry.block.workshop.tutor
                    ),
                    None
                ),
            }
            for day in days_of_week
        ]
        for block_number in num_blocks
    ]
    return schedule_table, num_blocks


# Función auxiliar: Determinar horario y talleres disponibles
def get_schedule_and_workshops(student):
    """
    Devuelve (bloques, talleres) filtrados según grado y colectivos,
    incluyendo Preescolar cuando student.grade <= 0 (PJ, J, T).
    """
    tipos = get_student_level_types(student) + ['collective']

    bloques = (
        Block.objects
             .filter(workshop__type__in=tipos)
             .select_related('workshop')
             .annotate(student_count=Count('students'))
    )

    talleres = Workshop.objects.filter(type__in=tipos)

    return bloques, list(talleres)


def student_schedule(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    schedule, workshops = get_schedule_and_workshops(student)

    # Si se pasa el workshop_id en la URL, actualizar el taller base
    workshop_id = request.GET.get('workshop_id')
    if workshop_id:
        try:
            workshop = Workshop.objects.get(id=workshop_id)
            student.workshop = workshop
            student.save()
        except Workshop.DoesNotExist:
            pass

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    student_schedule = (
        Schedule.objects
        .filter(student=student)
        .select_related('block', 'block__workshop', 'block__workshop__tutor', 'block__workshop__tutor__user')
    )
    is_mixed_grade = student.grade == 5
    level_types = get_student_level_types(student)

    schedule_table = []
    primary_schedule_table = []
    highschool_schedule_table = []
    num_blocks = range(1, 1)
    primary_num_blocks = range(1, 1)
    highschool_num_blocks = range(1, 1)

    if is_mixed_grade:
        primary_schedule_table, primary_num_blocks = build_level_schedule_table(
            student_schedule, days_of_week, 'primary'
        )
        highschool_schedule_table, highschool_num_blocks = build_level_schedule_table(
            student_schedule, days_of_week, 'high_school'
        )
    else:
        schedule_table, num_blocks = build_level_schedule_table(
            student_schedule, days_of_week, level_types[0]
        )

    context = {
        "student": student,
        "schedule_table": schedule_table,
        "primary_schedule_table": primary_schedule_table,
        "highschool_schedule_table": highschool_schedule_table,
        "days_of_week": days_of_week,
        "num_blocks": num_blocks,
        "primary_num_blocks": primary_num_blocks,
        "highschool_num_blocks": highschool_num_blocks,
        "is_mixed_grade": is_mixed_grade,
        "workshops": workshops,
    }

    return render(request, "schedules/student_schedule.html", context)




# schedules/utils.py


def get_block_capacity(workshops, day, block_number, block_type):
    """
    Agrega a cada workshop un atributo .current_capacity
    con el número de estudiantes asignados a ese bloque.
    """
    for w in workshops:
        # buscamos el bloque concreto para este workshop, día y número
        block = Block.objects.filter(
           workshop=w,
           day=day,
           block_number=block_number,
           type=block_type
       ).first()
        # si existe, contamos los estudiantes en ese bloque; si no, 0
        w.current_capacity = block.students.count() if block else 0


@login_required
def select_workshop(request, student_id, day, block_number):
    student = get_object_or_404(Student, student_id=student_id)
    _, workshops = get_schedule_and_workshops(student)
    allowed_block_types = get_student_level_types(student)

    block_type = request.GET.get('type')
    if block_type not in allowed_block_types:
        block_type = allowed_block_types[0]

    workshops = [w for w in workshops if w.type in ('collective', block_type)]
    get_block_capacity(workshops, day, block_number, block_type)

    if request.method == "POST":
        # nos aseguramos de recibirlo también en el form
        block_type = request.POST.get('type', block_type)
        if block_type not in allowed_block_types:
            block_type = allowed_block_types[0]

        workshop_id = request.POST.get('workshop')
        workshop = get_object_or_404(Workshop, workshop_id=workshop_id)

        # filtramos blocks POR TIPO también
        block = Block.objects.filter(
            block_number=block_number,
            day=day,
            workshop=workshop,
            type=block_type
        ).first()

        # calculamos capacidad
        if workshop.type == 'collective':
            if block_type == 'preschool' and workshop.max_capacity_aux_preschool:
                capacity = workshop.max_capacity_aux_preschool
            elif block_type == 'high_school' and workshop.max_capacity_aux:
                capacity = workshop.max_capacity_aux
            else:
                capacity = workshop.max_capacity
        else:
            capacity = workshop.max_capacity

        if not block or block.students.count() >= capacity:
            return render(request, 'schedules/select_workshop.html', {
                'student': student,
                'student_id': student_id,
                'workshops': workshops,
                'day': day,
                'block_number': block_number,
                'block_type': block_type,
                'error': f'Capacidad máxima ({capacity}) o bloque no existe.',
            })

    
        old_blocks = Block.objects.filter(
            students=student,
            day=day,
            block_number=block_number,
            type=block_type
        )
        for ob in old_blocks:
            ob.students.remove(student)
        
        Schedule.objects.filter(
            student=student,
            block__day=day,
            block__block_number=block_number,
            block__type=block_type
        ).delete()
        # ——————————————————————————————

        # creamos la nueva asignación
        Schedule.objects.create(student=student, block=block)
        block.students.add(student)

        return HttpResponseRedirect(reverse('student_schedule', args=[student_id]))

    # GET: enviamos block_type al template
    return render(request, 'schedules/select_workshop.html', {
        'student': student,
        'student_id': student_id,
        'workshops': workshops,
        'day': day,
        'block_number': block_number,
        'block_type': block_type,
    })



def select_block(request, tutor_id, day, block_number):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    blocks = Block.objects.filter(day=day, block_number=block_number)

    return render(request, 'schedules/students_by_block.html', {
        'tutor': tutor,
        'blocks': blocks,
        'day': day,
        'block_number': block_number,
    })



def students_in_block(request, tutor_id, day, block_number):
    from students.models import Attendance
    from django.utils import timezone
    import datetime
    
    block_type = request.GET.get("type")
    valid_level_types = {"primary", "high_school", "preschool"}
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    block = Block.objects.filter(
        day=day,
        block_number=block_number,
        type=block_type,
        workshop__tutor=tutor
    ).first()
    if not block:
        raise Http404("Bloque no encontrado")

    print(f"DEBUG BLOCK: ID={block.block_id}, Type={type(block)}, PK={block.pk}")
    
    # SIMULACIÓN DE TIEMPO: HAKUNA MATATA (Mañana es otro día)
    # today = timezone.now().date()
    today = timezone.now().date() + datetime.timedelta(days=1)
    print(f"DEBUG TIME TRAVEL: Hoy es {today}")

    if request.method == "POST":
        # Crear/actualizar registros de Attendance en lugar de student.status
        for student in block.students.all():
            key = f"status_{student.student_id}"
            new_status = request.POST.get(key)
            if new_status:
                Attendance.objects.update_or_create(
                    student=student,
                    block=block,
                    date=today,
                    defaults={
                        'status': new_status,
                        'marked_by': request.user
                    }
                )
        messages.success(request, "Asistencia registrada correctamente")
        return redirect(request.path + f"?type={block_type}")

    # GET: Obtener attendance de hoy para todos los estudiantes del bloque en UNA sola consulta
    students = block.students.all().order_by('lastname', 'name')
    
    # Traer todos los registros de attendance para este bloque y fecha
    attendances = Attendance.objects.filter(
        block=block,
        date=today,
        student__in=students
    ).select_related('student', 'marked_by')

    # Crear mpeo: student_id -> attendance_record
    attendance_map = {a.student_id: a for a in attendances}

    students_with_attendance = []
    for student in students:
        attendance = attendance_map.get(student.student_id)
        students_with_attendance.append({
            'student': student,
            'attendance': attendance,
            'current_status': attendance.status if attendance else 'neutral'
        })
    
    # Ordenar: ausentes primero, luego por apellido
    students_with_attendance.sort(
        key=lambda x: (
            0 if x['current_status'] == 'absent' else 1,
            x['student'].lastname,
            x['student'].name
        )
    )

    # Tipo de nivel para filtrar estudiantes en el buscador del modal.
    # Prioridad: tipo recibido en URL -> tipo del bloque -> tipo del taller.
    search_block_type = (
        block_type
        if block_type in valid_level_types
        else block.type if block.type in valid_level_types
        else block.workshop.type if block.workshop.type in valid_level_types
        else "primary"
    )

    return render(request, "schedules/students_in_block.html", {
        "tutor": tutor,
        "tutor_id": tutor.tutor_id,
        "block": block,
        "block_id": block.block_id, # Added block_id
        "block_id_fixed": block.block_id, # Explicitly passing ID
        "block_number": block.block_number,
        "block_day": block.day,
        "workshop": block.workshop,
        "search_block_type": search_block_type,
        "students_with_attendance": students_with_attendance,
        "today": today,
    })


@login_required
@require_POST
def clear_block_students(request, tutor_id, block_id):
    """
    Desvincula todos los estudiantes de un bloque específico de un tutor.
    - Conserva historial de asistencia (Attendance).
    - Limpia ambas fuentes de asignación (Schedule y Block.students).
    """
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    block = get_object_or_404(
        Block.objects.select_related("workshop"),
        block_id=block_id,
        workshop__tutor=tutor,
    )

    m2m_count = block.students.count()

    with transaction.atomic():
        # Elimina asignaciones explícitas del bloque para evitar inconsistencias.
        schedule_deleted, _ = Schedule.objects.filter(block=block).delete()
        # Limpia la relación M2M usada en vistas de bloque/capacidad/asistencia.
        block.students.clear()

    if m2m_count == 0 and schedule_deleted == 0:
        messages.info(request, "El bloque ya estaba vacío; no había estudiantes para desvincular.")
    else:
        messages.success(
            request,
            (
                f"Bloque limpiado correctamente. "
                f"Estudiantes desvinculados (M2M): {m2m_count}. "
                f"Asignaciones eliminadas (Schedule): {schedule_deleted}."
            ),
        )

    redirect_url = (
        reverse("student_in_block", args=[tutor.tutor_id, block.day, block.block_number])
        + f"?type={block.type}"
    )
    return HttpResponseRedirect(redirect_url)




@login_required
def delete_workshop(request, student_id, day, block_number, block_type):
    if request.method != 'POST':
        return redirect('student_schedule', student_id)

    student = get_object_or_404(Student, student_id=student_id)

    # Borra registros intermedios filtrando también por el tipo de bloque
    Schedule.objects.filter(
        student=student,
        block__day=day,
        block__block_number=block_number,
        block__type=block_type
    ).delete()

    # Quita la relación M2M de Block.students de forma segura, respetando el tipo
    block = Block.objects.filter(
        students=student,
        day=day,
        block_number=block_number,
        type=block_type
    ).first()
    if block:
        block.students.remove(student)

    messages.success(request, "Taller eliminado correctamente.")
    return redirect('student_schedule', student_id)


@login_required
def block_attendance_history(request, block_id):
    """
    Muestra el historial de asistencia de un bloque específico.
    Últimos 30 días de registros agrupados por fecha.
    """
    from students.models import Attendance
    from django.utils import timezone
    from datetime import timedelta
    from itertools import groupby
    
    block = get_object_or_404(Block, block_id=block_id)
    
    # Últimos 30 días
    date_from = timezone.now().date() - timedelta(days=30)
    attendances = (
        Attendance.objects
        .filter(block=block, date__gte=date_from)
        .select_related('student', 'marked_by')
        .order_by('-date', 'student__lastname', 'student__name')
    )
    
    # Agrupar por fecha y calcular estadísticas
    history_data = []
    for date, group in groupby(attendances, key=lambda a: a.date):
        group_list = list(group)
        stats = {
            'total': len(group_list),
            'present': len([a for a in group_list if a.status == 'present']),
            'absent': len([a for a in group_list if a.status == 'absent']),
        }
        history_data.append({
            'date': date,
            'attendances': group_list,
            'stats': stats
        })
    
    return render(request, 'schedules/block_attendance_history.html', {
        'block': block,
        'history_data': history_data,
        'date_from': date_from,
    })


@login_required
def ajax_search_students(request):
    query = request.GET.get('q', '')
    block_type = request.GET.get('block_type', 'primary')
    
    if not query:
        return JsonResponse({'results': []})
    
    # Filter by grade level
    if block_type == 'preschool':
        grade_filter = Q(grade__lte=0)
    elif block_type == 'high_school':
        grade_filter = Q(grade__gte=5)
    else: # primary
        grade_filter = Q(grade__gt=0, grade__lte=5)
        
    students = Student.objects.filter(
        grade_filter,
        Q(name__icontains=query) | Q(lastname__icontains=query) | Q(id_number__icontains=query)
    )[:10]
    
    results = []
    for s in students:
        results.append({
            'id': s.student_id,
            'text': f"{s.name} {s.lastname} (ID: {s.id_number})"
        })
        
    return JsonResponse({'results': results})


@login_required
def add_student_to_block(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    student_id = request.POST.get('student_id')
    block_id = request.POST.get('block_id')

    if not student_id or not block_id:
        return JsonResponse(
            {'success': False, 'error': 'Faltan datos obligatorios (student_id o block_id).'},
            status=400
        )

    try:
        student_id = int(student_id)
        block_id = int(block_id)
    except (TypeError, ValueError):
        return JsonResponse(
            {'success': False, 'error': 'student_id o block_id inválido.'},
            status=400
        )
    
    student = get_object_or_404(Student, student_id=student_id)
    block = get_object_or_404(Block, block_id=block_id)
    
    # Check if student is already in a block at the SAME time, day and level
    existing_schedule = Schedule.objects.filter(
        student=student,
        block__day=block.day,
        block__block_number=block.block_number,
        block__type=block.type
    ).first()
    
    if existing_schedule:
        # Conflict found
        return JsonResponse({
            'success': False,
            'conflict': True,
            'workshop_name': existing_schedule.block.workshop.name,
            'student_name': f"{student.name} {student.lastname}",
            'student_schedule_url': reverse('student_schedule', args=[student.student_id])
        })
    
    # Check capacity
    capacity = 25
    w = block.workshop
    if w.type == 'collective':
        if block.type == 'preschool' and w.max_capacity_aux_preschool:
            capacity = w.max_capacity_aux_preschool
        elif block.type == 'high_school' and w.max_capacity_aux:
            capacity = w.max_capacity_aux
        else:
            capacity = w.max_capacity
    else:
        capacity = w.max_capacity

    if block.students.count() >= capacity:
        return JsonResponse({
            'success': False,
            'error': f'Capacidad máxima ({capacity}) alcanzada.'
        })

    # No conflict, add student
    Schedule.objects.create(student=student, block=block)
    block.students.add(student)
    
    return JsonResponse({'success': True})
