from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    path('create/', views.create_workshop, name='create_workshop'),
    path('list/', views.list_workshops, name='list_workshops'),
    path('<int:workshop_id>/students/', views.students_by_workshop, name='students_by_workshop'),
    path('blocks/', views.show_blocks, name='show_blocks')
]
