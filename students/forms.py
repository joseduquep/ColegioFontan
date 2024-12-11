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
            'workshop'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'id_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de identificación'}),
            'autonomy_level': forms.Select(attrs={'class': 'form-control'}),
            'extended_vacation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'workshop': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number and id_number < 0:
            raise forms.ValidationError("El número de identificación no puede ser negativo.")
        return id_number
