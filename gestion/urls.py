from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # Rutas principales
    path('', views.dashboard, name='dashboard'),    
    path('agregar-cuenta/', views.agregar_cuenta, name='agregar_cuenta'),
]
