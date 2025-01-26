from django import forms
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 
            'lastname', 
            'id_number', 
            'autonomy_level', 
            'grade', 
            'workshop',
            'rotation_workshop'
        ]
        labels = {
            'name': 'Nombre',
            'lastname': 'Apellido',
            'id_number': 'Número de identificación',
            'autonomy_level': 'Nivel de autonomía',
            'grade': 'Grado',
            'workshop': 'Taller',
            'rotation_workshop': 'Taller de rotación'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su apellido'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su número de identificación'}),
            'autonomy_level': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'workshop': forms.Select(attrs={'class': 'form-control'}),
            'rotation_workshop': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el taller de rotación'}),
        }

    # Validación personalizada si se necesita
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        
        # Convertir id_number a string si es un número entero
        id_number = str(id_number)
        
        # Verificar la longitud del número de identificación
        if len(id_number) < 6:
            raise forms.ValidationError("El número de identificación debe tener al menos 6 dígitos.")
        
        return id_number
