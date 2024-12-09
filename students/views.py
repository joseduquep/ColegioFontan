from django.shortcuts import render, redirect
from .models import Student
from workshops.models import Workshop
from django.db.models import Q

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
