from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  # Ajustar si utilizas este formulario
# from .forms import CustomErrorList  # Si necesitas este también, ya lo tienes arriba

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
            return redirect('students.main_menu')

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
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})
    else:
        form = CustomUserCreationForm()
        template_data['form'] = form
        return render(request, 'accounts/signup.html', {'template_data': template_data})


@login_required
def profile_view(request):
    # Muestra la información del usuario actualmente autenticado
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    # Permite editar la información del usuario
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Asegúrate de que la URL de profile se llame 'profile'
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
