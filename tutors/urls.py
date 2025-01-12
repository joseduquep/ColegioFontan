from django.urls import path
from . import views


urlpatterns = [
    path('tutors_list/', views.tutors_list, name='tutors.tutors_list'),
    path('<int:tutor_id>/schedule/', views.tutor_schedule, name='tutor_schedule'),
    path('register_tutor/', views.register_tutor, name='tutors.register_tutor'),
    path('modify/tutor/<int:tutor_id>/', views.modify_tutor, name='tutors.modify_tutor'),
    path('delete/confirm/<int:tutor_id>/', views.confirm_delete_tutor, name='tutors.confirm_delete_tutor'),
    path('delete/<int:tutor_id>/', views.delete_tutor, name='tutors.delete_tutor'),
]
