from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Dispositivo, Reciclaje
import random
import json
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count


# Creación del login

def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'app/login.html')


# definicion de registro y autenticación

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe')
            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                messages.success(request, 'Cuenta creada correctamente, inicia sesión')
                return redirect('login')
        else:
            messages.error(request, 'Las contraseñas no coinciden')

    return render(request, 'app/register.html')


# Definición de inicio y dashboard y logout


@login_required
def dashboard(request):
    return render(request, 'app/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')



# se registra el dispositivo y se genera un correo con codigo aleatorio y unico

@login_required
def registrar_dispositivo(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        ubicacion = request.POST.get("ubicacion")
        direccion = request.POST.get("direccion")
        correo = request.POST.get("correo")

        import uuid
        codigo_unico = str(uuid.uuid4()).replace("-", "")[:10]

        # Verificar que no exista en BD
        
        while Dispositivo.objects.filter(codigo_unico=codigo_unico).exists():
            codigo_unico = str(uuid.uuid4()).replace("-", "")[:10]

        # se guarda en el dispositivo
        
        Dispositivo.objects.create(
            nombre=nombre,
            ubicacion=ubicacion,
            direccion=direccion,
            correo=correo,
            codigo_unico=codigo_unico
        )

        # Mensaje para el correo
        mensaje = f"""
¡Hola!

Tu dispositivo ha sido registrado exitosamente. 

Aquí está tu código único para reciclaje:

🔐 CÓDIGO: {codigo_unico}

⚠ IMPORTANTE:
• Este código es válido UNA SOLA VEZ.
• No lo compartas con nadie.
• Lo usarás en el apartado “Registrar Reciclaje”.

Datos ingresados:
• Nombre: {nombre}
• Ubicación: {ubicacion}
• Dirección: {direccion}

¡Gracias por aportar al proyecto GreenPoints! 💚🌱
"""

        # Se envia el correo
        send_mail(
            subject="Código de Reciclaje - GreenPoints",
            message=mensaje,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[correo],
            fail_silently=False,
        )

        return redirect('inicio')

    return render(request, "app/registrar_dispositivo.html")



# se ganan puntos a traves que se hace un registro en el reciclaje

@login_required
def registrar_reciclaje(request):
    if request.method == "POST":

        codigo_ingresado = request.POST.get("codigo_dispositivo")

        # validadción del correo unico
        
        try:
            dispositivo = Dispositivo.objects.get(codigo_unico=codigo_ingresado)
        except Dispositivo.DoesNotExist:
            messages.error(request, "El código ingresado NO es válido.")
            return redirect("registrar_reciclaje")

        # se verifica si ya fue usado
        if Reciclaje.objects.filter(codigo_usado=codigo_ingresado).exists():
            messages.error(request, "Este código YA fue usado una vez.")
            return redirect("registrar_reciclaje")

        # Se rellena datos en un formulario
        
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo")
        telefono = request.POST.get("telefono")
        tipo = request.POST.get("tipo_material") # tipo    
        peso = request.POST.get("peso_kg")
        foto = request.FILES.get("foto")

        # se crean puntos aleatorios y se canjea como unico
        puntos = random.randint(15, 60)

        codigo_canje = str(uuid.uuid4()).replace("-", "")[:8]

        # se registra en la base de datos
        Reciclaje.objects.create(
            dispositivo=dispositivo,
            codigo_usado=codigo_ingresado,
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            tipo_material=tipo,  
            peso_kg=peso,
            foto=foto,
            puntos=puntos,
            codigo_canje=codigo_canje
        )

        # Enviar correo
        mensaje = f"""
¡Gracias por reciclar! ♻️💚

Tu reciclaje ha sido registrado correctamente.

Has obtenido: ⭐ {puntos} PUNTOS

Aquí tienes tu código de canje (válido una sola vez):
Así que consérvalo de forma segura.

 CÓDIGO DE CANJE: {codigo_canje}

Tipo de reciclaje: {tipo}

Continúa reciclando para ayudar a reducir la contaminación y construir un planeta más verde. 
Acércate a tu punto de recolección más cercano para seguir depositando tus materiales y ganar aún más recompensas.

¡Gracias por ser parte del cambio! 💚
GreenPoints => Juntos por un futuro sostenible.
"""

        send_mail(
            subject="Puntos obtenidos - GreenPoints",
            message=mensaje,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[correo],
            fail_silently=False,
        )

        messages.success(request, "Reciclaje registrado correctamente.")
        return redirect('inicio')

    return render(request, "app/registrar_reciclaje.html")


# Inicio de datos + grafica interactiva


@login_required
def inicio(request):
   
    total_puntos = Reciclaje.objects.aggregate(total=Sum('puntos'))['total'] or 0

    total_registros = Reciclaje.objects.count()

    # Conteo por tipo de material (para donut)
    materiales_qs = Reciclaje.objects.values('tipo_material').annotate(
        cantidad=Count('id'),
        kilos=Sum('peso_kg')
    ).order_by('-cantidad')

    # Conservar en listas para JS
    
    materiales_labels = []
    materiales_counts = []
    materiales_kilos = []
    for row in materiales_qs:
        materiales_labels.append(row['tipo_material'] or 'No definido')
        materiales_counts.append(row['cantidad'] or 0)
        kilos = row['kilos'] or 0
        materiales_kilos.append(float(kilos))

    # Evolución de puntos por fecha — agrupado por día
    
    try:
        puntos_por_dia_qs = Reciclaje.objects.extra({
            'dia': "date(date(fecha_registro))"
        }).values('dia').annotate(total_puntos=Sum('puntos')).order_by('dia')

        puntos_por_dia = [(str(item['dia']), item['total_puntos'] or 0) for item in puntos_por_dia_qs]
    except Exception:
        qs = Reciclaje.objects.all().order_by('fecha_registro')
        tmp = {}
        for r in qs:
            d = r.fecha_registro.date().isoformat()
            tmp.setdefault(d, 0)
            tmp[d] += (r.puntos or 0)
        puntos_por_dia = sorted(tmp.items())

    chart_dates = [d for d, _ in puntos_por_dia]
    chart_points = [v for _, v in puntos_por_dia]

   
# Estos datos fueron recopilados a traves del ministerio de medio ambiente 

    arboles_salvados = 180000         
    co2_reducido = 5500                
    agua_conservada = 12000000        

    # Total kilos sigue existiendo SOLO para no romper el template
    total_kilos = 0

 
    # Se crearon niveles (tipos categorias) donde se escalan segun la cantidad de puntos
    
    niveles = [
        {'nombre': 'Sembrador', 'min': 0, 'max': 99},
        {'nombre': 'Recolector', 'min': 100, 'max': 299},
        {'nombre': 'Guardabosques', 'min': 300, 'max': 599},
        {'nombre': 'EcoHéroe', 'min': 600, 'max': 999},
        {'nombre': 'Leyenda Verde', 'min': 1000, 'max': 999999},
    ]

    nivel_actual = None
    siguiente_nivel = None
    progreso = 0
    for n in niveles:
        if total_puntos >= n['min'] and total_puntos <= n['max']:
            nivel_actual = n
            break
    if not nivel_actual:
        nivel_actual = niveles[-1]

    idx = next((i for i, x in enumerate(niveles) if x['nombre'] == nivel_actual['nombre']), 0)
    if idx < len(niveles) - 1:
        siguiente = niveles[idx + 1]
        rango = siguiente['min'] - nivel_actual['min']
        progreso = min(100, int(((total_puntos - nivel_actual['min']) / rango) * 100)) if rango > 0 else 100
        siguiente_nivel = siguiente
    else:
        progreso = 100
        siguiente_nivel = None

   
    residuos_desviados_ton = 1200
    reduccion_plastico_playas_kg = 75000
    material_reutilizado_kg = 950000

    context = {
        'total_puntos': total_puntos,
        'total_registros': total_registros,
        'materiales_labels': json.dumps(materiales_labels),
        'materiales_counts': json.dumps(materiales_counts),
        'materiales_kilos': json.dumps(materiales_kilos),
        'chart_dates': json.dumps(chart_dates),
        'chart_points': json.dumps(chart_points),

       
        'arboles_salvados': arboles_salvados,
        'co2_reducido': co2_reducido,
        'agua_conservada': agua_conservada,

      
        'total_kilos': total_kilos,

        'nivel_actual': nivel_actual,
        'progreso': progreso,
        'siguiente_nivel': siguiente_nivel,
        'niveles': niveles,

      
        'residuos_desviados_ton': residuos_desviados_ton,
        'reduccion_plastico_playas_kg': reduccion_plastico_playas_kg,
        'material_reutilizado_kg': material_reutilizado_kg,
    }

    return render(request, 'app/inicio.html', context)
