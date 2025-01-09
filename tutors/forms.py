from django import forms
from .models import Tutor
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TutorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['student'] 
        labels = {
            'student': 'Estudiante',
        }
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
        }

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo electrónico'}),
        }