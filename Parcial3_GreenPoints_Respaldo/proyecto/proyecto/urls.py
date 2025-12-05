from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', include('app.urls')),  # Rutas de la app
    path('admin/', admin.site.urls),

]
