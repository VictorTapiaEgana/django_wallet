from django.shortcuts import redirect
from django.urls import path, re_path
from . import views

app_name = 'gestion'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # Rutas principales
    path('', views.dashboard, name='dashboard'),    
    path('agregar-cuenta/', views.agregar_cuenta, name='agregar_cuenta'),
    path('administrar-cuentas/', views.administrar_cuentas, name='administrar_cuentas'),
    path('eliminar-cuenta/<int:cuenta_id>/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('actualizar-cuenta/<int:cuenta_id>/', views.actualizar_cuenta, name='actualizar_cuenta'),
    path('transferencias/', views.transferencias, name='transferencias'),



    re_path(r'^.*$', views.pagina_404_personalizada),
]
