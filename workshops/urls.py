from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    path('create/', views.create_workshop, name='create_workshop'),
    path('list/', views.list_workshops, name='list_workshops'),
]

