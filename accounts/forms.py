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
        widget=forms.RadioSelect,
        label="¿Eres Tutor?"
    )
    photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Por favor sube una foto de perfil (solo si eres tutor)."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilos del formulario
        for fieldname in ['username', 'password1', 'password2', 'email', 'cedula']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        cleaned_data = super().clean()
        is_tutor = cleaned_data.get('is_tutor')
        photo = cleaned_data.get('photo')

        # Validar foto si el usuario es tutor
        if is_tutor == 'yes' and not photo:
            self.add_error('photo', 'La foto es obligatoria si eres tutor.')

        # Configuración para staff si es tutor
        self.instance.is_staff = (is_tutor == 'yes')

        return cleaned_data

    def save(self, commit=True):
        """
        Guarda el formulario y crea un tutor si es necesario.
        """
        user = super().save(commit=False)

        # Guardamos el usuario
        if commit:
            user.save()

        # Si es tutor, crear la instancia de Tutor
        if self.cleaned_data.get('is_tutor') == 'yes':
            tutor = Tutor(
                user=user,
                photo=self.cleaned_data.get('photo')  # Guardamos la foto
            )
            tutor.save()

        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'cedula', 'password1', 'password2', 'is_tutor', 'photo']


class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))
