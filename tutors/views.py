from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from workshops.models import Workshop, Block
from tutors.models import Tutor
from schedules.models import Schedule
from django.contrib import messages



def tutors_list(request):
    query = request.GET.get('query', '').strip()  # Elimina espacios en blanco en la búsqueda
    workshops = Workshop.objects.all()

    if query:
    # Dividir la query en palabras clave separadas por espacios
        keywords = query.split()

    # Crear un filtro dinámico para buscar en nombre y apellido
        filters = Q()
        for keyword in keywords:
            filters |= Q(user__first_name__icontains=keyword) | Q(user__last_name__icontains=keyword)
    
    # Aplicar el filtro
        tutors = Tutor.objects.filter(filters)

    else:
        tutors = Tutor.objects.all()

    return render(request, 'tutors/tutors_list.html', {
        'workshops': workshops,
        'tutors': tutors,
        'query': query,
        'search_type': 'tutors',
    })


def tutor_schedule(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)

    schedule = {
        "Monday_Thursday": ["7:40-8:40", "9:10-10:20", "10:40-11:50", "12:30-1:30"],
        "Friday": ["7:40-8:40", "9:10-10:20", "10:40-11:50"],
    }
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Definir bloques por día para primaria y bachillerato
    blocks_per_day = {
        "Monday": 4,
        "Tuesday": 4,
        "Wednesday": 4,
        "Thursday": 4,
        "Friday": 3,
    }

    # Generar horario de Bachillerato (solo bloques de tipo high_school)
    highschool_blocks = Block.objects.filter(workshop__tutor=tutor, type="high_school").select_related("workshop")
    tutor_schedule_table = []
    for block_number in range(1, 5):  # Solo hasta 4 bloques para Bachillerato
        row = []
        for day in days_of_week:
            if block_number > blocks_per_day[day]:
                row.append({"day": day, "block_number": None, "workshop": None})
            else:
                block_entry = highschool_blocks.filter(block_number=block_number, day=day).first()
                row.append({
                    "day": day,
                    "block_number": block_number,
                    "workshop": block_entry.workshop.name if block_entry else None,
                })
        tutor_schedule_table.append(row)

    # Generar horario de Primaria (solo bloques de tipo primary)
    primary_blocks = Block.objects.filter(workshop__tutor=tutor, type="primary").select_related("workshop")
    primary_schedule_table = []
    for block_number in range(1, 6):  # Hasta 5 bloques para Primaria
        row = []
        for day in days_of_week:
            # Validar el límite de bloques para viernes y días regulares
            if (day == "Friday" and block_number > 4) or (day != "Friday" and block_number > 5):
                row.append({"day": day, "block_number": None, "workshop": None})
            else:
                block_entry = primary_blocks.filter(block_number=block_number, day=day).first()
                row.append({
                    "day": day,
                    "block_number": block_number,
                    "workshop": block_entry.workshop.name if block_entry else None,
                })
        primary_schedule_table.append(row)

    has_primary = tutor.workshops.filter(type="primary").exists()
    has_highschool = tutor.workshops.filter(type="high_school").exists()
    has_collective = tutor.workshops.filter(type="collective").exists()

    context = {
        "tutor": tutor,
        "tutor_id": tutor_id,
        "tutor_schedule_table": tutor_schedule_table,
        "days_of_week": days_of_week,
        "primary_schedule_table": primary_schedule_table,
        "has_primary": has_primary,
        "has_highschool": has_highschool,
        "has_collective": has_collective,
    }

    return render(request, "schedules/tutor_schedule.html", context)




def modify_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    workshops = Workshop.objects.all()

    if request.method == 'POST':
        # Actualizar datos del usuario asociado
        user = tutor.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Actualizar talleres asignados al tutor
        workshop_ids = request.POST.getlist('workshops')  # Lista de IDs de talleres seleccionados
        valid_workshop_ids = [wid for wid in workshop_ids if wid.strip()]  # Filtrar IDs válidos
        tutor.workshops.set(Workshop.objects.filter(workshop_id__in=valid_workshop_ids))

        tutor.save()
        messages.success(request, "¡Tutor modificado exitosamente!")
        return redirect('tutors.tutors_list')

    return render(request, 'tutors/modify_tutor.html', {
        'tutor': tutor,
        'workshops': workshops,
    })



def confirm_delete_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    return render(request, 'tutors/confirm_delete_tutor.html', {'tutor': tutor})


def delete_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    if request.method == 'POST':
        tutor.delete()
        messages.success(request, f"El tutor {tutor.user.first_name} {tutor.user.last_name} ha sido eliminado.")
        return redirect('tutors.tutors_list')
    return redirect('tutors.modify_tutor', tutor_id=tutor_id)
