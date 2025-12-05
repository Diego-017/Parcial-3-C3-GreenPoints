import threading
import time
from .notificacions import enviar_notificaciones

def iniciar_notificador():
    def run():
        while True:
            enviar_notificaciones()
            time.sleep(15)  # cada 1 hora

    hilo = threading.Thread(target=run, daemon=True)
    hilo.start()
