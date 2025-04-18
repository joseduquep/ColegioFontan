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

@login_required
def student_list(request):
    query = request.GET.get('query', '').strip()  # Elimina espacios en blanco en la búsqueda
    workshops = Workshop.objects.all()


    if query:
        keywords = query.split()

    # Crear un filtro dinámico para buscar en nombre y apellido
        filters = Q()
        for keyword in keywords:
            filters |= Q(name__icontains=keyword) | Q(lastname__icontains=keyword)
    
    # Aplicar el filtro
        students = Student.objects.filter(filters)

    else:
        students = Student.objects.all()

    # Paginación: Dividimos en grupos de 30 estudiantes
    paginator = Paginator(students, 30)  # 30 estudiantes por página
    page_number = request.GET.get('page')  # Página actual
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/student_list.html', {
        'workshops': workshops,
        'students': page_obj,  # Pasamos solo la página actual
        'query': query,
        'search_type': 'students',
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
        # Actualizar los datos del estudiante
        student.name = request.POST.get('name', student.name)
        student.lastname = request.POST.get('lastname', student.lastname)
        student.id_number = request.POST.get('id_number', student.id_number)
        student.autonomy_level = request.POST.get('autonomy_level', student.autonomy_level)
        student.grade = request.POST.get('grade', student.grade)
        student.rotation_workshop = request.POST.get('rotation_workshop', student.rotation_workshop)
        student.extended_vacation = 'extended_vacation' in request.POST
        

        # Actualizar el taller base si se selecciona
        workshop_id = request.POST.get('workshop')
        if workshop_id:
            workshop = get_object_or_404(Workshop, workshop_id=workshop_id)

            # Verificar si el taller tiene capacidad disponible
            current_student_count = Student.objects.filter(workshop=workshop).count()
            if current_student_count < workshop.max_capacity:
                student.workshop = workshop
                student.save()
                messages.success(request, f"Taller base actualizado a {workshop.name}.")
            else:
                messages.error(
                    request,
                    f"El taller '{workshop.name}' ha alcanzado su capacidad máxima ({workshop.max_capacity})."
                )
    # Agregar rango de grados al contexto
    grades_range = range(1, 12)

    return render(request, 'students/modify_student.html', {
        'student': student,
        'workshops': workshops,
        'grades_range': grades_range,  # Pasamos el rango aquí
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

@login_required
def absent_students(request):
    
    workshops = Workshop.objects.all()
    students = Student.objects.filter(status='absent')

    
    paginator = Paginator(students, 30)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/absent_students.html', {
        'workshops': workshops,
        'students': page_obj,  
    })