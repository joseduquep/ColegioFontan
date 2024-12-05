from django.shortcuts import render
from .models import Student
from workshops.models import Workshop

def main_menu(request):
    workshops = Workshop.objects.all()
    query = request.GET.get('q', '')  # Obtenemos la consulta de búsqueda
    if query:
        students = Student.objects.filter(nombre__icontains=query)  # Filtramos por nombre (ajustar si es necesario)
    else:
        students = Student.objects.all()

    return render(request, 'students/main_menu.html', {'workshops': workshops,'students': students, 'query': query})
