from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MinLengthValidator
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(validators=[MinLengthValidator(10)])
    precio = models.DecimalField(max_digits=10, decimal_places=2,
                                 validators=[MinValueValidator(Decimal('0.01'))])
    imagen = models.ImageField(upload_to='productos/')
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False, help_text='Aparece en el Home')
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(validators=[MinLengthValidator(10)])
    imagen = models.ImageField(upload_to='servicios/')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Slide(models.Model):
    titulo = models.CharField(max_length=100)
    subtitulo = models.CharField(max_length=200, blank=True)
    imagen = models.ImageField(upload_to='slides/')
    orden = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.titulo


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PREPARACION', 'En preparación'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Pedido #{self.pk}'


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.asunto} - {self.nombre}'