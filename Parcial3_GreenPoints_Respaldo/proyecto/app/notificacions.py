import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import ConfigNotificaciones
from .models import Reciclaje
from django.db.models import Sum

#  LISTAS DE MENSAJES ALEATORIOS

MENSAJES_METAS = [
    "¡Sigue así! Estás cada vez más cerca de tu meta. 🌱",
    "Tu esfuerzo está dando frutos. ¡No te detengas! 💪",
    "¡Vas excelente! Solo un poco más para cumplir tu meta. 🚀",
    "¡Tu constancia te está llevando directo a tus metas! 🌟",
    "Cada día estás más cerca de lograrlo. ¡No aflojes! 🔥",
    "Si sigues así, tu meta será tu próximo logro. 💚",
    "Un paso más, un avance más. ¡Tú puedes! ✨",
    "La meta no está lejos… ¡te estás acercando rápido! 🚀",
    "Hoy es un buen día para avanzar hacia tus metas. 💪",
]

MENSAJES_RECOMPENSAS = [
    "¡Vamos por más recompensas! 🎁",
    "Tus puntos están creciendo, ¡pronto podrás canjear algo grande!",
    "¿Ya viste el catálogo? Puede haber algo para ti 👀",
    "¡Tus puntos tienen poder! Sigue así y reclama algo genial. 🛍️",
    "Estás acumulando puntos como un campeón. 🏆",
    "¿Listo para tu próxima recompensa? Tú decides cuándo. 🎉",
    "Tu próximo premio está más cerca de lo que crees. 👏",
    "¡Sigue reciclando y desbloquea recompensas increíbles! 🔓",
    "El catálogo siempre tiene algo esperando por ti… 😉",
]

MENSAJES_MOTIVACION = [
    "¡Cada acción cuenta para salvar el planeta! 🌍",
    "Pequeños cambios hacen grandes diferencias. 💚",
    "Gracias por reciclar, estás marcando la diferencia. ♻️",
    "Tu compromiso inspira a otros. ¡Bien hecho! ⭐",
    "Lo que haces hoy tiene impacto mañana. 🌎💫",
    "Gracias por reciclar, ¡eres parte del cambio! ♻️💚",
    "Tu acción de hoy hace un futuro más verde. 🍃",
    "Reciclar es un acto simple con un impacto poderoso. 🌱",
    "¡Tu esfuerzo suma! Y el planeta lo agradece. 🌏🤝",
    "Sigue adelante, cada gesto ecológico cuenta. 🌼",
    "El mundo necesita más personas como tú. 💚✨",
]

MENSAJES_NIVELES = [
    "¡Estás a poco de subir de nivel! 🌱",
    "Tu próxima insignia está cerca, ¡no te rindas! 🏆",
    "¡Nivel casi alcanzado! Sigue reciclando. 🔥",
    "¡No te detengas! El siguiente nivel será tuyo pronto. 🎯",
    "Estás brillando, sigue así y subirás de nivel. ⭐",
    "¡Tu progreso es increíble! El nuevo nivel está al alcance. 🚀",
    "Avanzas rápido… ¡ese nivel será tuyo en nada! ⚡",
    "Tu dedicación te está llevando directo hacia la cima. 🏔️",
    "Un poco más de esfuerzo y desbloqueas el siguiente nivel. 🔓",
]


#  FUNCIÓN PRINCIPAL QUE ENVÍA NOTIFICACIONES

def enviar_notificaciones():
    usuarios = User.objects.all()

    for user in usuarios:
        config = ConfigNotificaciones.objects.filter(usuario=user).first()
        if not config:
            continue
        #  Freno general: si todo está apagado, no mandar nada
        if not (config.noti_metas or config.noti_recompensas or config.noti_niveles):
            continue
        
        # Puntos actuales
        puntos_usuario = Reciclaje.objects.filter(
            correo=user.email
        ).aggregate(total=Sum('puntos'))['total'] or 0

        # Elegir mensaje según switches
        mensajes_a_enviar = []

        if config.noti_metas:
            mensajes_a_enviar.append(random.choice(MENSAJES_METAS))

        if config.noti_recompensas:
            mensajes_a_enviar.append(random.choice(MENSAJES_RECOMPENSAS))

        if config.noti_niveles:
            mensajes_a_enviar.append(random.choice(MENSAJES_NIVELES))

        # Siempre mezclamos con un motivacional
        mensajes_a_enviar.append(random.choice(MENSAJES_MOTIVACION))

        if not mensajes_a_enviar:
            continue  # No hay notificaciones activas

        # Elegir uno aleatorio
        mensaje_final = random.choice(mensajes_a_enviar)

        # Enviar correo
        send_mail(
            subject="Notificación GreenPoints😎",
            message=f"{mensaje_final}\n\nTus puntos actuales: {puntos_usuario}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
