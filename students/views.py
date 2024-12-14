from django.shortcuts import render, redirect
from .models import Student
from workshops.models import Workshop
from django.db.models import Q
from django.contrib import messages
from .forms import StudentRegistrationForm

def main_menu(request):
    workshops = Workshop.objects.all()
    query = request.GET.get('query')  # Obtenemos la consulta de búsqueda
    if query:
        students = Student.objects.filter(
        Q(name__icontains=query) | Q(lastname__icontains=query)
    )
    else:
        students = Student.objects.all()

    return render(request, 'students/main_menu.html', {'workshops': workshops,'students': students, 'query': query})


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Estudiante registrado exitosamente!")
            return redirect('students.main_menu')
    else:
        form = StudentRegistrationForm()
    return render(request, 'students/register_student.html', {'form': form})