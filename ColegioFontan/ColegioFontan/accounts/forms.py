from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User  # Modelo User de Django
from tutors.models import Tutor  # Importar modelo Tutor

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Por favor ingrese un correo electrónico válido."
    )
    cedula = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Por favor ingrese su número de cédula."
    )
    is_tutor = forms.ChoiceField(
        choices=[('yes', 'Sí'), ('no', 'No')],
        widget=forms.RadioSelect,
        label="¿Eres Tutor?"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar estilos uniformemente a todos los campos
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        is_tutor = cleaned_data.get('is_tutor')

        # Configurar `is_staff` según el rol de tutor
        self.instance.is_staff = (is_tutor == 'yes')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Si es tutor, crear la instancia de Tutor
        if self.cleaned_data.get('is_tutor') == 'yes':
            Tutor.objects.create(user=user)

        return user

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cedula', 'password1', 'password2', 'is_tutor']
