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
