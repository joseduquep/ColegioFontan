from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    path('create/', views.create_workshop, name='create_workshop'),
    path('list/', views.list_workshops, name='list_workshops'),
    path('<int:workshop_id>/students/', views.students_by_workshop, name='students_by_workshop'),
    path('blocks/', views.show_blocks, name='show_blocks'),
    path('delete/confirm/<int:workshop_id>/', views.confirm_delete_workshop, name='confirm_delete_workshop'),
    path('delete/<int:workshop_id>/', views.delete_workshop, name='delete_workshop'),
    path('modify/<int:workshop_id>/', views.modify_workshop, name='modify_workshop'),
]
