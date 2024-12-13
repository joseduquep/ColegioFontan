from django.urls import path
from . import views

urlpatterns = [
    
    path('<int:student_id>/schedule/', views.student_schedule, name='student_schedule'),
    path('<int:student_id>/add_workshop/', views.add_workshop, name='schedule_add_workshop'),
    path('add_workshop/<int:student_id>/', views.add_workshop, name='add_workshop'),
    path('select_workshop/<int:student_id>/<str:day>/<int:block>/', views.select_workshop, name='select_workshop'),
]
