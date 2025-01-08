from django.urls import path
from . import views

urlpatterns = [
    path('select_workshop/<int:student_id>/<str:day>/<int:block_number>/', views.select_workshop, name='select_workshop'),
    path('<int:student_id>/schedule/', views.student_schedule, name='student_schedule'),
    path('select_block/<int:tutor_id>/<str:day>/<int:block_number>/', views.select_block, name='select_block'),
    path('<int:tutor_id>/<str:day>/<int:block_number>/students/', views.students_in_block, name='student_in_block'),
]
