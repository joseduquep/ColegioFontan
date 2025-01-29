from django.urls import path
from . import views


urlpatterns = [
    path('student_list/', views.student_list, name='students.student_list'),
    path('register/', views.register_student, name='students.register_student'),
    path('modify/<int:student_id>/', views.modify_student, name='students.modify_student'),
    path('delete/<int:student_id>/', views.delete_student, name='students.delete_student'),
    path('delete/confirm/<int:student_id>/', views.confirm_delete_student, name='students.confirm_delete_student'),
    path('absent_students/', views.absent_students, name='students.absent_students'),


]
