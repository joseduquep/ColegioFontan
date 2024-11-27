from django.shortcuts import render
from . import models

def main_menu(request):
    
    #query = not query
    #estudiantes = Estudiante.objects.all()
    return render(request, 'students/main_menu.html')


#def search(request):
    query = request.GET.get('query')
    #estudiantes = Estudiante.objects.filter(nombre__icontains=query)
    return render(request, 'estudiantes/home.html', {'estudiantes': estudiantes, 'query': query})
# Create your views here.
