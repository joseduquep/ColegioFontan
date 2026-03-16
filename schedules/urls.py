from django.urls import path
from . import views

urlpatterns = [
    path('select_workshop/<int:student_id>/<str:day>/<int:block_number>/', views.select_workshop, name='select_workshop'),
    path('<int:student_id>/schedule/', views.student_schedule, name='student_schedule'),
    path('select_block/<int:tutor_id>/<str:day>/<int:block_number>/', views.select_block, name='select_block'),
    path('<int:tutor_id>/<str:day>/<int:block_number>/students/', views.students_in_block, name='student_in_block'),
    path(
        '<int:tutor_id>/block/<int:block_id>/clear-students/',
        views.clear_block_students,
        name='clear_block_students'
    ),
    path('delete-workshop/<int:student_id>/<str:day>/<int:block_number>/<str:block_type>/',
        views.delete_workshop,
        name='delete_workshop'
    ),
    path('block/<int:block_id>/attendance-history/', views.block_attendance_history, name='block_attendance_history'),
    path('ajax/search-students/', views.ajax_search_students, name='ajax_search_students'),
    path('ajax/add-student-to-block/', views.add_student_to_block, name='add_student_to_block'),
]
