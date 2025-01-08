from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentRegistrationForm
from .models import Student
from workshops.models import Workshop
from django.db.models import Q

def student_list(request):
    workshops = Workshop.objects.all()
    query = request.GET.get('query')  # Obtenemos la consulta de búsqueda

    # Corregimos la lógica de búsqueda
    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) | Q(lastname__icontains=query)
        )
    else:
        students = Student.objects.all()

    return render(request, 'students/student_list.html', {'workshops': workshops, 'students': students, 'query': query})

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
