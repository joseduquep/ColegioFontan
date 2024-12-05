from django.urls import path
from . import views

urlpatterns = [
    # Ruta para la página principal de horarios (puede ser un índice o lista de estudiantes)
    path('', views.schedule_index, name='schedule_index'),

    # Ruta para ver el horario de un estudiante específico
    path('<int:student_id>/schedule/', views.student_schedule, name='student_schedule'),

    # Ruta para actualizar el horario de un estudiante
    path('<int:student_id>/update/', views.update_schedule, name='update_schedule'),
]
