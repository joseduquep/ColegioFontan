from django.contrib import admin
from .models import Student
# Register your models here.

class studentAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

admin.site.register(Student, studentAdmin)