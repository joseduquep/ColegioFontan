from django.contrib import admin
from .models import Workshop, Block

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('name', 'tutor', 'max_capacity')  # Campos que quieres mostrar en la lista
    search_fields = ('name',)  # Habilita la búsqueda por nombre
    list_filter = ('tutor',)  # Filtro lateral por tutor
    ordering = ('name',)  # Ordena por nombre

# Definir un BlockAdmin para mostrar el ID y otros detalles
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('block_id', 'workshop', 'day', 'start_time', 'end_time')  # Mostrar block_id
    list_filter = ('workshop', 'day')  # Puedes agregar filtros adicionales si lo deseas
    search_fields = ('workshop__name',)  # Habilita la búsqueda por nombre de taller
    ordering = ('block_id',)  # Ordena por block_id
