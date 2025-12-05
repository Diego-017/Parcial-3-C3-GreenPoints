from .models import ConfigNotificaciones

def modo_oscuro(request):
    if request.user.is_authenticated:
        config = ConfigNotificaciones.objects.filter(usuario=request.user).first()
        if config:
            return {'dark_mode': config.modo_oscuro}
    return {'dark_mode': False}
