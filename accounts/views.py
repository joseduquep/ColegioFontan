
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  
from django.shortcuts import render, redirect, get_object_or_404
from tutors.models import Tutor
from workshops.models import Workshop
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib import messages
from students.models import Student
from django.contrib.auth import update_session_auth_hash

def login(request):
    
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.home')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')
    
def signup(request):
    template_data = {'title': 'Sign Up'}
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil se ha registrado correctamente!')
            return redirect('home.home')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})
    else:
        form = CustomUserCreationForm()
        template_data['form'] = form
        return render(request, 'accounts/signup.html', {'template_data': template_data})

@login_required
def tutor_profile(request):
    # Verifica si el usuario tiene un perfil de tutor
    if hasattr(request.user, 'tutor_profile'):
        tutor = get_object_or_404(Tutor, user=request.user)
        # Talleres no asignados o ya asignados al tutor
        unassigned_workshops = Workshop.objects.filter(tutor__isnull=True) | Workshop.objects.filter(tutor=tutor)
        context = {
            'user': request.user,
            'tutor': tutor,
            'unassigned_workshops': unassigned_workshops,
        }
    else:
        # Usuario sin perfil de tutor
        user = get_object_or_404(User, pk=request.user.pk)
        context = {
            'user': user,
        }

    return render(request, 'accounts/profile.html', context)




@login_required
def edit_tutor_profile(request):
    if hasattr(request.user, 'tutor_profile'):
        # Usuario es tutor
        tutor = get_object_or_404(Tutor, user=request.user)

        if request.method == 'POST':
            # Actualizar datos del usuario
            tutor.user.username = request.POST.get('username', tutor.user.username)
            tutor.user.first_name = request.POST.get('name', tutor.user.first_name)
            tutor.user.last_name = request.POST.get('lastname', tutor.user.last_name)
            tutor.user.email = request.POST.get('email', tutor.user.email)
            tutor.user.save()

            # Cambio de contraseña
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if current_password and new_password:
                if not request.user.check_password(current_password):
                    messages.error(request, "La contraseña actual es incorrecta.")
                elif new_password != confirm_password:
                    messages.error(request, "Las nuevas contraseñas no coinciden.")
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # Mantener sesión activa
                    messages.success(request, "Contraseña cambiada correctamente.")

            # Obtener taller seleccionado
            selected_workshop_id = request.POST.get('workshop')
            if selected_workshop_id:
                # Desasignar taller previo del tutor si existe
                current_workshop = Workshop.objects.filter(tutor=tutor).first()
                if current_workshop:
                    current_workshop.tutor = None
                    current_workshop.save()

                # Asignar nuevo taller al tutor
                selected_workshop = get_object_or_404(Workshop, workshop_id=selected_workshop_id)
                selected_workshop.tutor = tutor
                selected_workshop.save()

            return redirect('tutor_profile')

    else:
        # Usuario no es tutor
        user = get_object_or_404(User, pk=request.user.pk)

        if request.method == 'POST':
            # Actualizar datos del usuario
            user.username = request.POST.get('username', user.username)
            user.first_name = request.POST.get('name', user.first_name)
            user.last_name = request.POST.get('lastname', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()

            # Cambio de contraseña
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if current_password and new_password:
                if not user.check_password(current_password):
                    messages.error(request, "La contraseña actual es incorrecta.")
                elif new_password != confirm_password:
                    messages.error(request, "Las nuevas contraseñas no coinciden.")
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Mantener sesión activa
                    messages.success(request, "Contraseña cambiada correctamente.")

            return redirect('tutor_profile')

    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'tutor': tutor if hasattr(request.user, 'tutor_profile') else None,
    })