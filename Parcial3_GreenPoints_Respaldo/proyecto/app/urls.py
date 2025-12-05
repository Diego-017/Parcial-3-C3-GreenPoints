from django.urls import path
from app import views
from django.conf.urls.static import static  #imagenes
from django.conf import settings
from . import views

urlpatterns = [
    
    path("", views.landing_page, name="INICIO"), 
    
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

    # recompensas     
    path('canjear/', views.canjear_recompensas, name='canjear'),
    path('premio/<int:pk>/confirmar/', views.confirmar_canje, name='confirmar_canje'),
    
    #PERFIL Y EDTIAR PERFIL
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    # ACTIVIDAD RECIENTE
    path('actividad/', views.actividad_reciente, name='actividad_reciente'),
    # CONFIGURACION
    path("configuracion/", views.configuracion, name="configuracion"),


]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)