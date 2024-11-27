from django.urls import path
from . import views



urlpatterns = [
    path('main_menu/', views.main_menu, name='main_menu'),
    #path('search/', views.search, name='search'),
]
