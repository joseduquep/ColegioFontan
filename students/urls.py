from django.urls import path
from . import views


urlpatterns = [
    path('student_list/', views.student_list, name='students.student_list'),
    path('register/', views.register_student, name='students.register_student'),
    path('modify/<int:student_id>/', views.modify_student, name='students.modify_student'),
    path('delete/<int:student_id>/', views.delete_student, name='students.delete_student'),
    path('delete/confirm/<int:student_id>/', views.confirm_delete_student, name='students.confirm_delete_student'),
    # absent_students URL removed - use block-based attendance instead
    path('<int:student_id>/schedule/pdf/', views.student_schedule_pdf, name='student_schedule_pdf'),

]
