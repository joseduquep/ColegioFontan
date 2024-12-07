from django.urls import path
from . import views

urlpatterns = [
    path('show/', views.show_tutors, name='tutors.show_tutors'),
    path('<int:tutor_id>/schedule/', views.tutor_schedule, name='tutor_schedule'),
]
