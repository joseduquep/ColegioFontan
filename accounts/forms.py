from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User  # Usamos el modelo User de Django
from tutors.models import Tutor  # Asegúrate de importar el modelo Tutor

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
    photo = forms.ImageField(
        required=False,  # No es obligatorio por defecto
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Por favor sube una foto de perfil (solo si eres tutor)."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el campo `photo` obligatorio solo si es tutor
        if self.initial.get('is_tutor') == 'yes':
            self.fields['photo'].required = True
        else:
            self.fields['photo'].required = False

        # Actualizamos los estilos del formulario
        for fieldname in ['username', 'password1', 'password2', 'email', 'cedula']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        cleaned_data = super().clean()
        is_tutor = cleaned_data.get('is_tutor')
        photo = cleaned_data.get('photo')

        # Si el usuario es tutor, asegurarse de que se haya subido una foto
        if is_tutor == 'yes' and not photo:
            self.add_error('photo', 'La foto es obligatoria si eres tutor.')

        # Si el usuario es tutor, activamos is_staff
        if is_tutor == 'yes':
            self.instance.is_staff = True
        else:
            self.instance.is_staff = False

        return cleaned_data

    def save(self, commit=True):
        """
        Guarda el formulario. Si el usuario es un tutor, también guarda
        la foto en el modelo Tutor.
        """
        user = super().save(commit=False)

        # Guardamos el usuario primero
        if commit:
            user.save()

        # Si es un tutor, guardamos la foto en el modelo Tutor
        if self.cleaned_data.get('is_tutor') == 'yes':
            tutor = Tutor(user=user)
            tutor.photo = self.cleaned_data.get('photo')
            tutor.save()

        return user

    class Meta:
        model = User  # Usamos el modelo User de Django
        fields = ['username', 'email', 'cedula', 'password1', 'password2']


class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))
