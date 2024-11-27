from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User  # Usamos el modelo User de Django

# Personalizamos el formulario de creación de usuario
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
        widget=forms.RadioSelect,  # Esto lo convierte en un input tipo radio
        label="¿Eres Tutor?"
    )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # Eliminamos los textos de ayuda por defecto
        for fieldname in ['username', 'password1', 'password2', 'email', 'cedula']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        cleaned_data = super().clean()
        is_tutor = cleaned_data.get('is_tutor')

        # Si el usuario es tutor, activamos is_staff
        if is_tutor == 'yes':
            self.instance.is_staff = True
        else:
            self.instance.is_staff = False

        return cleaned_data
    
    class Meta:
        model = User  # Usamos el modelo User de Django
        fields = ['username', 'email', 'cedula', 'password1', 'password2']

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))
