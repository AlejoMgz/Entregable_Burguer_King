from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (Categoria, Producto, Servicio, Slide,
                         Cliente, Pedido, DetallePedido)

CATEGORIAS = [
    ('Combos', 'Tu hamburguesa favorita con papas y bebida.'),
    ('Hamburguesas', 'Carne a la parrilla, como a ti te gusta.'),
    ('Pollo', 'Crocante por fuera, jugoso por dentro.'),
    ('Acompañamientos', 'Para completar tu pedido.'),
    ('Bebidas', 'Refrescantes y bien frías.'),
    ('Postres', 'El toque dulce final.'),
]

# (categoría, nombre, descripción, precio, archivo de imagen, destacado)
# Las imágenes van en: media/productos/<archivo>
PRODUCTOS = [
    # ---- Combos ----
    ('Combos', 'Combo Whopper',
     'Whopper con papas fritas medianas y gaseosa a elección.',
     '36900', 'combo-whopper.jpg', True),           # IMAGEN: media/productos/combo-whopper.jpg
    ('Combos', 'Combo Crispy Chicken',
     'Sándwich de pollo crocante con papas fritas y gaseosa.',
     '31900', 'combo-crispy.jpg', False),           # IMAGEN: media/productos/combo-crispy.jpg
    ('Combos', 'Combo Junior',
     'Whopper Junior con papas pequeñas, bebida y sorpresa para los niños.',
     '24900', 'combo-junior.jpg', False),           # IMAGEN: media/productos/combo-junior.jpg
    # ---- Hamburguesas ----
    ('Hamburguesas', 'Whopper',
     'Carne de res a la parrilla, tomate, lechuga, mayonesa, pepinillos, cebolla y kétchup en pan con ajonjolí.',
     '26900', 'whopper.jpg', True),                 # IMAGEN: media/productos/whopper.jpg
    ('Hamburguesas', 'Whopper con Queso',
     'La clásica Whopper con una tajada de queso derretido encima.',
     '28900', 'whopper-queso.jpg', True),           # IMAGEN: media/productos/whopper-queso.jpg
    ('Hamburguesas', 'Doble Whopper',
     'Dos carnes a la parrilla con todos los ingredientes de la Whopper. Para los de gran apetito.',
     '36900', 'doble-whopper.jpg', True),           # IMAGEN: media/productos/doble-whopper.jpg
    ('Hamburguesas', 'Whopper Junior',
     'La versión pequeña de la Whopper, ideal para los más chicos.',
     '17900', 'whopper-junior.jpg', False),         # IMAGEN: media/productos/whopper-junior.jpg
    ('Hamburguesas', 'Cheeseburger',
     'Carne a la parrilla con queso, pepinillos, kétchup y mostaza.',
     '12900', 'cheeseburger.jpg', False),           # IMAGEN: media/productos/cheeseburger.jpg
    ('Hamburguesas', 'Bacon King',
     'Doble carne a la parrilla, queso y abundante tocineta ahumada.',
     '34900', 'bacon-king.jpg', False),             # IMAGEN: media/productos/bacon-king.jpg
    # ---- Pollo ----
    ('Pollo', 'Crispy Chicken',
     'Filete de pollo empanizado y crocante con lechuga y mayonesa en pan suave.',
     '21900', 'crispy-chicken.jpg', True),          # IMAGEN: media/productos/crispy-chicken.jpg
    ('Pollo', 'Long Chicken',
     'Filete de pollo crocante en pan alargado con lechuga y salsa cremosa.',
     '19900', 'long-chicken.jpg', False),           # IMAGEN: media/productos/long-chicken.jpg
    ('Pollo', 'Nuggets de Pollo x6',
     'Seis trozos de pollo empanizado con la salsa que prefieras.',
     '11900', 'nuggets-6.jpg', False),              # IMAGEN: media/productos/nuggets-6.jpg
    ('Pollo', 'Nuggets de Pollo x10',
     'Diez trozos de pollo empanizado, perfectos para compartir.',
     '17900', 'nuggets-10.jpg', False),             # IMAGEN: media/productos/nuggets-10.jpg
    # ---- Acompañamientos ----
    ('Acompañamientos', 'Papas Fritas',
     'Papas doradas y crocantes con sal, porción mediana.',
     '7900', 'papas-fritas.jpg', False),            # IMAGEN: media/productos/papas-fritas.jpg
    ('Acompañamientos', 'Aros de Cebolla',
     'Aros de cebolla empanizados, crujientes y calientes.',
     '8900', 'aros-cebolla.jpg', False),            # IMAGEN: media/productos/aros-cebolla.jpg
    # ---- Bebidas ----
    ('Bebidas', 'Gaseosa',
     'Gaseosa bien fría, elige tu sabor favorito.',
     '6900', 'gaseosa.jpg', False),                 # IMAGEN: media/productos/gaseosa.jpg
    ('Bebidas', 'Malteada de Vainilla',
     'Malteada cremosa de vainilla con crema batida.',
     '12900', 'malteada.jpg', False),               # IMAGEN: media/productos/malteada.jpg
    # ---- Postres ----
    ('Postres', 'Sundae de Chocolate',
     'Helado suave de vainilla bañado en salsa de chocolate.',
     '8900', 'sundae.jpg', False),                  # IMAGEN: media/productos/sundae.jpg
    ('Postres', 'Pay de Manzana',
     'Pay caliente y crocante relleno de manzana con canela.',
     '7900', 'pay-manzana.jpg', False),             # IMAGEN: media/productos/pay-manzana.jpg
]

# (nombre, descripción, archivo de imagen)
# Las imágenes van en: media/servicios/<archivo>
SERVICIOS = [
    ('Domicilio',
     'Recibe tu pedido caliente en la puerta de tu casa u oficina. Pídelo y nosotros lo llevamos.',
     'servicio-domicilio.jpg'),                     # IMAGEN: media/servicios/servicio-domicilio.jpg
    ('Para llevar',
     'Haz tu pedido en el mostrador y recógelo sin esperar. Rápido y fácil.',
     'servicio-para-llevar.jpg'),                   # IMAGEN: media/servicios/servicio-para-llevar.jpg
    ('Autoservicio',
     'Pide desde tu carro sin bajarte. Tu combo listo en pocos minutos.',
     'servicio-autoservicio.jpg'),                  # IMAGEN: media/servicios/servicio-autoservicio.jpg
    ('Comer en el restaurante',
     'Disfruta tus hamburguesas en un ambiente cómodo, ideal para ir en familia o con amigos.',
     'servicio-restaurante.jpg'),                   # IMAGEN: media/servicios/servicio-restaurante.jpg
    ('Fiestas infantiles',
     'Celebra el cumpleaños de tus hijos con juegos, combos infantiles y mucha diversión.',
     'servicio-fiestas.jpg'),                       # IMAGEN: media/servicios/servicio-fiestas.jpg
    ('Pedidos corporativos',
     'Almuerzos y eventos para empresas: grandes cantidades con entrega programada.',
     'servicio-corporativo.jpg'),                   # IMAGEN: media/servicios/servicio-corporativo.jpg
]

# (título, subtítulo, archivo de imagen, orden)
# Las imágenes van en: media/slides/<archivo>  (1920x600 px recomendado)
SLIDES = [
    ('¡Prueba la Whopper!', 'Carne a la parrilla, como a ti te gusta', 'slide1.jpg', 1),   # IMAGEN: media/slides/slide1.jpg
    ('Combos para compartir', 'Más sabor, mejor precio', 'slide2.jpg', 2),                 # IMAGEN: media/slides/slide2.jpg
    ('Pídelo a domicilio', 'Llega caliente a tu puerta', 'slide3.jpg', 3),                 # IMAGEN: media/slides/slide3.jpg
]

# Pedidos de ejemplo para el cliente demo: (estado, [(producto, cantidad), ...])
PEDIDOS = [
    ('ENTREGADO', [('Combo Whopper', 2), ('Sundae de Chocolate', 1)]),
    ('PREPARACION', [('Crispy Chicken', 1), ('Papas Fritas', 1), ('Gaseosa', 1)]),
    ('PENDIENTE', [('Nuggets de Pollo x10', 1), ('Malteada de Vainilla', 2)]),
]


class Command(BaseCommand):
    help = 'Carga categorías, productos, servicios, slides y pedidos de ejemplo.'

    @transaction.atomic
    def handle(self, *args, **options):
        cats = {}
        for nombre, desc in CATEGORIAS:
            cats[nombre], creada = Categoria.objects.get_or_create(
                nombre=nombre, defaults={'descripcion': desc, 'activa': True})

        for cat, nombre, desc, precio, archivo, destacado in PRODUCTOS:
            Producto.objects.get_or_create(nombre=nombre, defaults={
                'categoria': cats[cat], 'descripcion': desc, 'precio': Decimal(precio),
                'imagen': f'productos/{archivo}', 'disponible': True, 'destacado': destacado})

        for nombre, desc, archivo in SERVICIOS:
            Servicio.objects.get_or_create(nombre=nombre, defaults={
                'descripcion': desc, 'imagen': f'servicios/{archivo}', 'activo': True})

        for titulo, sub, archivo, orden in SLIDES:
            Slide.objects.get_or_create(titulo=titulo, defaults={
                'subtitulo': sub, 'imagen': f'slides/{archivo}', 'orden': orden, 'activo': True})

        # Cliente demo con pedidos de ejemplo
        user, creado = User.objects.get_or_create(username='cliente_demo', defaults={
            'first_name': 'Cliente', 'last_name': 'Demo', 'email': 'cliente@demo.com'})
        if creado:
            user.set_password('Cliente12345*')
            user.save()
        cliente, creado = Cliente.objects.get_or_create(user=user, defaults={
            'telefono': '3001234567', 'direccion': 'Calle 10 # 20-30, Medellín'})

        if not cliente.pedidos.exists():
            for estado, items in PEDIDOS:
                pedido = Pedido.objects.create(cliente=cliente, estado=estado, total=0)
                total = Decimal('0')
                for nombre, cantidad in items:
                    prod = Producto.objects.get(nombre=nombre)
                    DetallePedido.objects.create(pedido=pedido, producto=prod, cantidad=cantidad,
                                                 precio_unitario=prod.precio)
                    total += prod.precio * cantidad
                pedido.total = total
                pedido.save()

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Categoria.objects.count()} categorías, {Producto.objects.count()} productos, '
            f'{Servicio.objects.count()} servicios, {Slide.objects.count()} slides y '
            f'{Pedido.objects.count()} pedidos.'))