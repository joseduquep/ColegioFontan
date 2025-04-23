from django import forms
from .models import Workshop

# workshops/forms.py

class WorkshopForm(forms.ModelForm):
    max_capacity_aux = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Capacidad Bachillerato (colectivos)'
    )

    class Meta:
        model = Workshop
        fields = ['name', 'type', 'max_capacity', 'max_capacity_aux']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre del Taller',
            'type': 'Tipo de Taller',
            'max_capacity': 'Capacidad Primaria / Bachillerato (simples)',
        }
