from django.urls import path
from . import views



urlpatterns = [
    path('main_menu/', views.main_menu, name='students.main_menu'),
    path('register/', views.register_student, name='students.register_student'),
    #path('search/', views.search, name='search'),
]
