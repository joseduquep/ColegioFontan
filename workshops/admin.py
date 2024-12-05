from django.contrib import admin
from .models import Workshop
from .models import Block


    
@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('name', 'tutor', 'max_capacity')  # Campos que quieres mostrar en la lista
    search_fields = ('name',)  # Habilita la búsqueda por nombre
    list_filter = ('tutor',)  # Filtro lateral por tutor
    ordering = ('name',)  # Ordena por nombre


admin.site.register(Block)