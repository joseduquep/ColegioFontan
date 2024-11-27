from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from .forms import CustomUserCreationForm, CustomErrorList
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('main_menu')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')
    


from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from .forms import CustomUserCreationForm  # Asegúrate de que el formulario esté importado correctamente

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Guardamos el formulario y el nuevo usuario
            form.save()
            # Redirigimos al login después de un registro exitoso
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})
    
    else:
        form = CustomUserCreationForm()
        template_data['form'] = form
        return render(request, 'accounts/signup.html', {'template_data': template_data})

        
        

