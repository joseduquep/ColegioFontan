from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from workshops.models import Workshop, Block
from tutors.models import Tutor
from schedules.models import Schedule
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
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

from django.db.models import Count

@login_required
def tutor_schedule(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    blocks_per_day = {"Monday": 4, "Tuesday": 4, "Wednesday": 4, "Thursday": 4, "Friday": 3}

    # Traemos bloques con conteo
    highschool_blocks = (
        Block.objects
             .filter(workshop__tutor=tutor, type="high_school")
             .select_related("workshop")
             .annotate(student_count=Count("students"))
    )
    primary_blocks = (
        Block.objects
             .filter(workshop__tutor=tutor, type="primary")
             .select_related("workshop")
             .annotate(student_count=Count("students"))
    )

    # 📋 Tabla Bachillerato (1–4 bloques; viernes límite=3)
    tutor_schedule_table = []
    for block_number in range(1, 5):
        row = []
        for day in days_of_week:
            if block_number > blocks_per_day[day]:
                row.append({"day": day, "block_number": None, "workshop_name": None, "student_count": None, "max_capacity": None})
            else:
                entry = highschool_blocks.filter(block_number=block_number, day=day).first()
                if entry:
                    w = entry.workshop
                    cap = w.max_capacity_aux if (w.type == 'collective' and w.max_capacity_aux) else w.max_capacity
                    row.append({
                        "day": day,
                        "block_number": block_number,
                        "workshop_name": w.name,
                        "student_count": entry.student_count,
                        "max_capacity": cap,
                    })
                else:
                    row.append({"day": day, "block_number": None, "workshop_name": None, "student_count": None, "max_capacity": None})
        tutor_schedule_table.append(row)

    # 📋 Tabla Primaria (1–5 bloques; viernes límite=4 **cambio aquí**)
    primary_schedule_table = []
    for block_number in range(1, 6):
        row = []
        for day in days_of_week:
            # ahora viernes tiene hasta 4 bloques, resto hasta 5
            limit = 4 if day == "Friday" else 5
            if block_number > limit:
                row.append({"day": day, "block_number": None, "workshop_name": None, "student_count": None, "max_capacity": None})
            else:
                entry = primary_blocks.filter(block_number=block_number, day=day).first()
                if entry:
                    w = entry.workshop
                    row.append({
                        "day": day,
                        "block_number": block_number,
                        "workshop_name": w.name,
                        "student_count": entry.student_count,
                        "max_capacity": w.max_capacity,
                    })
                else:
                    row.append({"day": day, "block_number": None, "workshop_name": None, "student_count": None, "max_capacity": None})
        primary_schedule_table.append(row)

    context = {
        "tutor": tutor,
        "tutor_id": tutor_id,
        "days_of_week": days_of_week,
        "tutor_schedule_table": tutor_schedule_table,
        "primary_schedule_table": primary_schedule_table,
        "has_collective": tutor.workshops.filter(type="collective").exists(),
        "has_primary": tutor.workshops.filter(type="primary").exists(),
        "has_highschool": tutor.workshops.filter(type="high_school").exists(),
        "has_preschool": tutor.workshops.filter(type="preschool").exists(),
    }
    return render(request, "schedules/tutor_schedule.html", context)



@login_required
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


@login_required
def confirm_delete_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    return render(request, 'tutors/confirm_delete_tutor.html', {'tutor': tutor})

@login_required
def delete_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, tutor_id=tutor_id)
    if request.method == 'POST':
        tutor.delete()
        messages.success(request, f"El tutor {tutor.user.first_name} {tutor.user.last_name} ha sido eliminado.")
        return redirect('tutors.tutors_list')
    return redirect('tutors.modify_tutor', tutor_id=tutor_id)