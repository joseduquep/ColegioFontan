from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import Student
from workshops.models import Workshop
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import unicodedata
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from workshops.models import Block
from django.utils import timezone

def strip_accents(text: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()


def build_schedule_context(student):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    student_blocks = (
        Block.objects
             .filter(students=student)
             .select_related('workshop')
    )
    lookup = {(b.day, b.block_number): b for b in student_blocks}

    schedule_table = []
    # Ahora todos los días pueden tener hasta 5 bloques
    for num in range(1, 6):
        row = []
        for day in days_of_week:
            b = lookup.get((day, num))
            if b and b.workshop:
                row.append({
                    "block_number": num,
                    "workshop": b.workshop,
                    "tutor": b.workshop.tutor,
                })
            else:
                row.append({"block_number": None, "workshop": None, "tutor": None})
        schedule_table.append(row)

    return days_of_week, schedule_table

@login_required
def student_schedule_pdf(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    # 1) Obtenemos días y tabla
    days_of_week, schedule_table = build_schedule_context(student)

    # 2) Fecha y hora de generación
    generation_datetime = timezone.now().strftime("%d/%m/%Y %H:%M")

    # 3) Contexto para el template
    context = {
        "student": student,
        "days_of_week": days_of_week,
        "schedule_table": schedule_table,
        "generation_datetime": generation_datetime,
    }

    # 4) Render a HTML
    html = render_to_string("students/schedule_pdf.html", context)

    # 5) Creamos la respuesta PDF con nombre = student_id.pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{student.id_number}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generando PDF", status=500)
    return response


@login_required
def student_list(request):
    raw_q          = request.GET.get('query', '').strip()
    grade_param    = request.GET.get('grade')
    level          = request.GET.get('level')        # 'primary' o 'high_school'
    workshop_param = request.GET.get('workshop')
    view_mode      = request.GET.get('view', 'mosaic')

    # 1) Partimos del queryset base y aplicamos filtros estructurales
    qs = Student.objects.select_related('workshop').all()

    if grade_param:
        try:
            grade_int = int(grade_param)
            qs = qs.filter(grade=grade_int)
        except ValueError:
            pass  # Ignorar si no es un número válido

    if level == 'primary':
        qs = qs.filter(grade__lte=5)
    elif level == 'high_school':
        qs = qs.filter(grade__gt=5)
    elif level == 'preschool':
        qs = qs.filter(grade__lte=0)  # PJ, J, T (todos los preescolar)

    if workshop_param and workshop_param.isdigit():
        qs = qs.filter(workshop__workshop_id=int(workshop_param))

    # 2) Convertimos a lista para el filtrado/orden en Python
    students_list = list(qs)

    # 3) Si hay término de búsqueda, lo usamos para filtrar sin tildes
    if raw_q:
        q_norm = strip_accents(raw_q)
        students_list = [
            s for s in students_list
            if q_norm in strip_accents(s.lastname)
            or q_norm in strip_accents(s.name)
        ]

    # 4) Orden alfabético insensible a tildes
    students_list.sort(key=lambda s: (
        strip_accents(s.lastname),
        strip_accents(s.name)
    ))

    # 5) Paginación sobre la lista ya ordenada
    paginator     = Paginator(students_list, 30)
    students_page = paginator.get_page(request.GET.get('page'))

    # 6) Contexto para los selects
    grade_choices    = Student._meta.get_field('grade').choices
    workshop_choices = Workshop.objects.all()

    return render(request, 'students/student_list.html', {
        'students': students_page,
        'query': raw_q,
        'grade_choices': grade_choices,
        'selected_grade': int(grade_param) if (grade_param and grade_param.isdigit()) else None,
        'selected_level': level,
        'workshop_choices': workshop_choices,
        'selected_workshop': int(workshop_param) if (workshop_param and workshop_param.isdigit()) else None,
        'view_mode': view_mode,
    })

@login_required
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Aquí simplemente se guarda el estudiante. Si tienes algún tipo de validación
                # adicional, este es un buen lugar para hacerlo.
                form.save()
                messages.success(request, "¡Estudiante registrado exitosamente!")
                return redirect('students.student_list')
            except Exception as e:
                messages.error(request, f"Ocurrió un error al registrar al estudiante: {str(e)}")
                return redirect('students.register_student')
        else:
            messages.error(request, "Por favor, revisa los datos del formulario.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'students/register_student.html', {'form': form})

@login_required
def modify_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    workshops = Workshop.objects.all()

    if request.method == 'POST':
        # 1) Campos básicos
        student.name               = request.POST.get('name', student.name)
        student.lastname           = request.POST.get('lastname', student.lastname)
        student.id_number          = request.POST.get('id_number', student.id_number)
        student.autonomy_level     = int(request.POST.get('autonomy_level', student.autonomy_level))
        student.grade              = int(request.POST.get('grade', student.grade))
        student.rotation_workshop  = request.POST.get('rotation_workshop', student.rotation_workshop)
        student.extended_vacation  = 'extended_vacation' in request.POST
        student.general_data       = request.POST.get('general_data', student.general_data)

        # 2) Taller base
        workshop_id = request.POST.get('workshop')
        if workshop_id:
            workshop = get_object_or_404(Workshop, workshop_id=workshop_id)
            current_count = Student.objects.filter(workshop=workshop).count()
            if current_count < workshop.max_capacity:
                student.workshop = workshop
                messages.success(request, f"Taller base actualizado a «{workshop.name}».")
            else:
                messages.error(
                    request,
                    f"El taller «{workshop.name}» ha alcanzado su capacidad máxima ({workshop.max_capacity})."
                )
        else:
            student.workshop = None

        # 3) Guardar todos los cambios
        student.save()
        return redirect('students.student_list')

    # GET: preparar context
    grades_range = range(-3, 12)  # PJ (-3) hasta 11
    return render(request, 'students/modify_student.html', {
        'student': student,
        'workshops': workshops,
        'grades_range': grades_range,
    })


@login_required
def confirm_delete_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    return render(request, 'students/confirm_delete_student.html', {'student': student})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, f"El estudiante {student.name} {student.lastname} ha sido eliminado.")
        return redirect('students.student_list')  # Redirige a la lista de estudiantes
    return redirect('students.modify_student', student_id=student_id)  # Si no es POST, regresa a modificar


# absent_students view removed - attendance is now tracked per block
# Use block_attendance_history view in schedules app instead