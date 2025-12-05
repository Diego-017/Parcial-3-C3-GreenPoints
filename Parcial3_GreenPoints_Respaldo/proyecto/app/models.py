from django.db import models
from django.contrib.auth.models import User

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
    tipo_material = models.CharField(max_length=50)  
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    foto = models.ImageField(upload_to="evidencias/", null=True, blank=True)

    # Datos personales
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)

    # Puntos generados automáticamente
    puntos = models.IntegerField()
    
    # CANTIDADES
    cantidad = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Unico y nuevo
    codigo_canje = models.CharField(max_length=12, unique=True, editable=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    codigo_canje_usado = models.BooleanField(default=False)

    # HISTORIAL DE REGISTROS Y CANJEOS
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        import uuid

        # Generar código_usado si está vacío (solo en nuevos registros)
        if not self.codigo_usado:
            self.codigo_usado = uuid.uuid4().hex[:12].upper()

        # Generar codigo_canje si está vacío
        # Solo si es un registro positivo, no movimientos del sistema
        if not self.codigo_canje:
            self.codigo_canje = uuid.uuid4().hex[:12].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reciclaje de {self.nombre} ({self.puntos} pts)"



# CODIGO PARA CANJEAR RECOMPENSAS

class Premio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    puntos_necesarios = models.IntegerField()
    imagen = models.ImageField(upload_to='premios/', null=True, blank=True)

    def __str__(self):
        return self.nombre


# PERFIL

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return f"Perfil de {self.user.username}"

# ACTIVIDAD RECIENTE

class Canje(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    premio = models.ForeignKey(Premio, on_delete=models.CASCADE)
    fecha_canje = models.DateTimeField(auto_now_add=True)
    puntos_usados = models.IntegerField()

    def __str__(self):
        return f"{self.usuario.username} canjeó {self.premio.nombre}"


# NOTIFICACIONES

from django.db import models
from django.contrib.auth.models import User

class ConfigNotificaciones(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    noti_metas = models.BooleanField(default=False)
    noti_recompensas = models.BooleanField(default=False)
    noti_niveles = models.BooleanField(default=False)
    modo_oscuro = models.BooleanField(default=False)

    def __str__(self):
        return f"Config de {self.usuario.username}"
