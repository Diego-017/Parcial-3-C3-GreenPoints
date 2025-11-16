from django.db import models

from django.db import models
#REGISTRO DE DISPOSITIVO
class Dispositivo(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    correo = models.EmailField()
    codigo_unico = models.CharField(max_length=12, unique=True, editable=False)
    
    def __str__(self):
        return self.nombre

# CODIGOS PARA CANJEAR CON PUNTOS 

class Reciclaje(models.Model):
    # Relación con Dispositivo
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)

    # Guardar el código del dispositivo que se usó (para evitar que se repita)
    codigo_usado = models.CharField(max_length=12, unique=True)

    # Evidencia
    tipo_material = models.CharField(max_length=50)  # plástico, vidrio, aluminio, etc.
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    foto = models.ImageField(upload_to="evidencias/", null=True, blank=True)

    # Datos personales
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)

    # Puntos generados automáticamente
    puntos = models.IntegerField()

    # Código de canje (nuevo y único)
    codigo_canje = models.CharField(max_length=12, unique=True, editable=False)

    # Fecha automática
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reciclaje de {self.nombre} ({self.puntos} pts)"
