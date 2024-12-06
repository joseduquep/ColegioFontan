from django.shortcuts import render, get_object_or_404
from workshops.models import Workshop
from .models import Tutor

# Vista para mostrar los tutores y los workshops
def show_tutors(request):
    workshops = Workshop.objects.all()  # Obtener todos los workshops
    query = request.GET.get('q', '')  # Obtener la consulta de búsqueda
    if query:
        tutors = Tutor.objects.filter(nombre__icontains=query)  # Filtrar por nombre
    else:
        tutors = Tutor.objects.all()  # Obtener todos los tutores
    return render(request, 'tutors/show_tutors.html', {'workshops': workshops, 'tutors': tutors, 'query': query})

# Vista para mostrar el horario del tutor
def tutor_schedule(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)  # Obtener el tutor por ID o 404 si no existe
    return render(request, 'tutors/tutor_schedule.html', {'tutor': tutor})
