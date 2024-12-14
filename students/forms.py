from django import forms
from .models import Student
from workshops.models import Block

class StudentRegistrationForm(forms.ModelForm):
    blocks = forms.ModelMultipleChoiceField(
        queryset=Block.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
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

    def save(self, commit=True):
        student = super().save(commit=False)
        if commit:
            student.save()
            student.blocks.set(self.cleaned_data['blocks'])
        return student
