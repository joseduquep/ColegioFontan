from django.urls import path
from . import views


urlpatterns = [
    path('student_list/', views.student_list, name='students.student_list'),
    path('register/', views.register_student, name='students.register_student'),
]
