from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ConfigNotificaciones

@receiver(post_save, sender=User)
def crear_config(sender, instance, created, **kwargs):
    if created:
        ConfigNotificaciones.objects.create(usuario=instance)