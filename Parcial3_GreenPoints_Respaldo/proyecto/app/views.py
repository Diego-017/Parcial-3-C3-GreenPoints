from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Dispositivo, Reciclaje, Premio
import random
import json
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count

# Interfaz inicio

def landing_page(request):
    return render(request, 'index.html')


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
        cantidad = request.POST.get("cantidad")
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
            cantidad=cantidad,
            foto=foto,
            puntos=puntos,
            codigo_canje=codigo_canje,
            usuario=request.user     
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
Cantidad reciclada: {cantidad} unidades

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

#CANJEO RECOMPENSAS

@login_required
def canjear_recompensas(request):

    codigo_valido = False
    premios = None

    # Puntos reales del usuario
    puntos_usuario = Reciclaje.objects.filter(
        correo=request.user.email
    ).aggregate(Sum('puntos'))['puntos__sum'] or 0

    if request.method == "POST":
        codigo = request.POST.get("codigo")

        # Buscar código en Reciclaje
        try:
            rec = Reciclaje.objects.get(codigo_canje=codigo)
        except Reciclaje.DoesNotExist:
            messages.error(request, "El código ingresado NO existe.")
            return render(request, "app/canjear.html", {
                "catalogo_visible": False,
                "puntos": puntos_usuario
            })

        # Verificar si ya fue usado (nuevo campo)
        if rec.codigo_canje_usado:
            messages.error(request, "Este código YA fue utilizado.")
            return render(request, "app/canjear.html", {
                "catalogo_visible": False,
                "puntos": puntos_usuario
            })

        # No marcamos como usado hasta que realmente canjee un premio
        request.session["codigo_canje_valido"] = rec.codigo_canje

        messages.success(request, "Código válido. Ahora puedes ver el catálogo.")
        codigo_valido = True
        premios = Premio.objects.all()

    return render(request, "app/canjear.html", {
        "catalogo_visible": codigo_valido,
        "premios": premios,
        "puntos": puntos_usuario
    })
import uuid

@login_required
def confirmar_canje(request, pk):
    premio = Premio.objects.get(pk=pk)

    puntos_usuario = Reciclaje.objects.filter(
        correo=request.user.email
    ).aggregate(Sum('puntos'))['puntos__sum'] or 0

    if puntos_usuario < premio.puntos_necesarios:
        messages.error(request, "No tienes puntos suficientes para canjear este premio.")
        return redirect("canjear")

    codigo = request.session.get("codigo_canje_valido")

    if not codigo:
        messages.error(request, "No has validado ningún código.")
        return redirect("canjear")

    try:
        rec = Reciclaje.objects.get(codigo_canje=codigo)
    except Reciclaje.DoesNotExist:
        messages.error(request, "El código validado ya no existe.")
        return redirect("canjear")

    if rec.codigo_canje_usado:
        messages.error(request, "Este código ya fue utilizado para canjear.")
        return redirect("canjear")

    # Marcar el código original como usado
    rec.codigo_canje_usado = True
    rec.save()

    request.session.pop("codigo_canje_valido", None)

    #  evitar colisión en los UNIQUE
    unique_codigo_usado = f"CANJE-{uuid.uuid4().hex[:12]}"
    unique_codigo_canje_negativo = f"DESC-{uuid.uuid4().hex[:12]}"

    # crear movimiento de descuento
    Reciclaje.objects.create(
        nombre="Sistema",
        apellido="",
        correo=request.user.email,
        telefono="",
        tipo_material="Canje de premio",
        peso_kg=0,
        cantidad=0,
        puntos=-int(premio.puntos_necesarios),
        codigo_usado=unique_codigo_usado,
        codigo_canje=unique_codigo_canje_negativo,  
        dispositivo=Dispositivo.objects.first(),
        usuario=request.user,
    )
    # Registrar el CANJE REAL en su propio modelo
    Canje.objects.create(
    usuario=request.user,
    premio=premio,
    puntos_usados=premio.puntos_necesarios,
)


    send_mail(
        subject="Confirmación de Canje - GreenPoints",
        message=f"Has canjeado el premio: {premio.nombre}. ¡Gracias por reciclar!",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email],
        fail_silently=False,
    )
    messages.set_level(request, messages.DEBUG)
    return render(request, "app/canje_confirmado.html", {"premio": premio})


#PERFIL
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .profile_forms import PerfilForm

@login_required
def perfil(request):
    if request.method == "POST":
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid(): 
            form.save()
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)
        
    # Calcular puntos totales del usuario basado en su correo
    
    puntos_totales = Reciclaje.objects.filter(
        correo=request.user.email
    ).aggregate(total=Sum('puntos'))['total'] or 0
    return render(request, 'app/perfil.html', {'form': form,'puntos_totales': puntos_totales,})

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)

    return render(request, 'app/editar_perfil.html', {'form': form})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Reciclaje, Canje
# VERIFICAR TODOS LOS REGISTROS EN ACTIVIDAD RECIENTE
from django.contrib.auth.decorators import login_required
from .models import Reciclaje, Canje

@login_required
def actividad_reciente(request):

    # Historial de reciclaje (solo reciclaje real)
    historial_reciclaje = Reciclaje.objects.filter(
        usuario=request.user
        ).exclude(
    tipo_material="Canje de premio"
    ).order_by('-fecha_registro')

    # Historial de canjes (solo canje de premios)
    historial_canje = Canje.objects.filter(
        usuario=request.user
    ).order_by('-fecha_canje')

    return render(request, "app/actividad_reciente.html", {
        "historial_reciclaje": historial_reciclaje,
        "historial_canje": historial_canje,
    })



# NOTIFICACIONES

from django.contrib.auth.decorators import login_required
from .models import ConfigNotificaciones

@login_required
def configuracion(request):
    config, created = ConfigNotificaciones.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        config.noti_metas = request.POST.get("noti_metas") == "on"
        config.noti_recompensas = request.POST.get("noti_recompensas") == "on"
        config.noti_niveles = request.POST.get("noti_niveles") == "on"
        config.modo_oscuro = request.POST.get("modo_oscuro") == "on"
        config.save()

    return render(request, "app/configuracion.html", {"config": config})
