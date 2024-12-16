from django.urls import path
from . import views  # Ajusta según tu estructura

urlpatterns = [
    path('select_workshop/<int:student_id>/<str:day>/<int:block_number>/', views.select_workshop, name='select_workshop'),
    path('<int:student_id>/schedule/', views.student_schedule, name='student_schedule'),

    # Nueva ruta para tutores
    path('select_block/<int:tutor_id>/<str:day>/<int:block_number>/', views.select_block, name='select_block'),
]
