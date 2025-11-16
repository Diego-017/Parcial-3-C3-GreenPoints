from django.urls import path
from app import views

urlpatterns = [
    # LOGIN / REGISTRO
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # DASHBOARD / INICIO
    path('inicio/', views.inicio, name='inicio'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # DISPOSITIVOS
    path('registrar-dispositivo/', views.registrar_dispositivo, name='registrar_dispositivo'),
    
    # reciclaje
    
    path('registrar-reciclaje/', views.registrar_reciclaje, name='registrar_reciclaje'),


]


