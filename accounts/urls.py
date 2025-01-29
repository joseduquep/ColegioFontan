from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('profile/', views.tutor_profile, name='tutor_profile'),
    path('profile/edit/', views.edit_tutor_profile, name='edit_tutor_profile'),
]
