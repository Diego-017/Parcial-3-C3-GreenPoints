import os
import django

# CONFIGURAR EL PROYECTO DJANGO
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto.settings")
django.setup()

from app.models import Premio

# LISTA DE PREMIOS CON NOMBRE, DESCRIPCIÓN, PUNTOS E IMAGEN
premios = [
    ("Termo Eco 750ml", "Termo fabricado con aluminio reciclado.", 250, "premios/termo.jpg"),
    ("Camiseta Eco", "Camiseta hecha con fibras de plástico reciclado.", 400, "premios/camisa_eco.jpg"),
    ("Árbol donado", "Una organización siembra un árbol a tu nombre.", 200, "premios/arbol.jpg"),
    ("Bolsa reutilizable", "Bolsa de tela hecha de material reciclado.", 150, "premios/bolsa.jpg"),
    ("Botella purificadora", "Botella con filtro ecológico.", 550, "premios/botella_purificadora.jpg"),
    ("Vaso plegable", "Ideal para café o bebidas frías.", 220, "premios/vaso_reutilizable.jpg"),
    ("Cargador solar", "Cargador USB con panel solar.", 800, "premios/cargador_solar.jpg"),
    ("Kit de siembra", "Incluye semillas de hierbas o flores.", 300, "premios/kit_siembra.jpg"),
    ("Cubiertos de bambú", "Incluye cubiertos de bambú.", 350, "premios/estuche_reutilizable.jpg"),
    ("Jabón ecológico", "Hecho sin químicos dañinos.", 280, "premios/jabon_ecologico.jpg"),
    ("Taza ecológica", "Reutilizable, resistente y biodegradable.", 350, "premios/taza_ecologica.jpg"),
    ("Kit Zero Waste", "Incluye bolsa, termo y cubiertos eco.", 1000, "premios/kit_zero_waste.jpg"),
    ("Vela ecológica", "Vela ecológica de soya sin fragancias tóxicas.", 330, "premios/vela_ecologica.jpg"),
    ("Mini contenedor", "Perfecto para separar papel.", 240, "premios/mini_contenedor.jpg"),
    ("Desodorante natural", "Ecológico y biodegradable.", 320, "premios/desodorante_natural.jpg"),
    ("Encendedor solar", "Funciona solo con luz solar.", 600, "premios/encendedor_solar.jpg"),
]

# CREAR O ACTUALIZAR LOS PREMIOS
for nombre, descripcion, puntos, imagen in premios:
    obj, creado = Premio.objects.update_or_create(
        nombre=nombre,
        defaults={
            "descripcion": descripcion,
            "puntos_necesarios": puntos,
            "imagen": imagen
        }
    )
    print(("CREADO" if creado else "ACTUALIZADO"), nombre)

print("\n*** LISTO ✓ Premios cargados correctamente ***")
