from django.shortcuts import render
from .models import Student

def main_menu(request):
    query = request.GET.get('q', '')  # Obtenemos la consulta de búsqueda
    if query:
        students = Student.objects.filter(nombre__icontains=query)  # Filtramos por nombre (ajustar si es necesario)
    else:
        students = Student.objects.all()

    return render(request, 'students/main_menu.html', {'students': students, 'query': query})
