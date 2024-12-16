from django.contrib import admin
from .models import Tutor

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'student')  # Campos que quieres mostrar en el admin
    search_fields = ('user__username', 'student__name')  # Campos para buscar
    list_filter = ('student',)  # Opcional, para agregar filtros
