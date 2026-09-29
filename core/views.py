from django.shortcuts import render

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm, MensajeForm
from .models import (Categoria, Producto, Servicio, Slide, Cliente,
                     Pedido, DetallePedido)


def home(request):
    return render(request, 'core/home.html', {
        'slides': Slide.objects.filter(activo=True),
        'destacados': Producto.objects.filter(disponible=True, destacado=True)[:6],
        'servicios': Servicio.objects.filter(activo=True)[:3],
    })


def servicios(request):
    return render(request, 'core/servicios.html', {
        'servicios': Servicio.objects.filter(activo=True)})


def productos(request):
    categorias = Categoria.objects.filter(activa=True)
    lista = Producto.objects.filter(disponible=True, categoria__activa=True)
    cat = request.GET.get('categoria', '')
    if cat.isdigit():
        lista = lista.filter(categoria_id=int(cat))
    return render(request, 'core/productos.html', {
        'productos': lista, 'categorias': categorias, 'cat_activa': cat})


def contacto(request):
    form = MensajeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu mensaje fue enviado. ¡Gracias por escribirnos!')
            return redirect('contacto')
        messages.error(request, 'Revisa los campos marcados e inténtalo de nuevo.')
    return render(request, 'core/contacto.html', {'form': form})


# ---------- Login y registro ----------
class LoginPersonalizado(LoginView):
    template_name = 'core/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        if self.request.user.is_staff:
            return reverse('panel_dashboard')
        return reverse('home')

    def form_valid(self, form):
        messages.success(self.request, f'Bienvenido, {form.get_user().username}.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada con éxito! Ya puedes hacer pedidos.')
            return redirect('home')
        messages.error(request, 'No se pudo crear la cuenta. Revisa los errores.')
    return render(request, 'core/registro.html', {'form': form})


# ---------- Carrito (guardado en la sesión) ----------
def _items_carrito(request):
    carrito = request.session.get('carrito', {})
    items, total = [], Decimal('0')
    for p in Producto.objects.filter(pk__in=carrito.keys(), disponible=True):
        cantidad = carrito[str(p.pk)]
        subtotal = p.precio * cantidad
        items.append({'producto': p, 'cantidad': cantidad, 'subtotal': subtotal})
        total += subtotal
    return items, total


def carrito(request):
    items, total = _items_carrito(request)
    return render(request, 'core/carrito.html', {'items': items, 'total': total})


@require_POST
def carrito_agregar(request, pk):
    producto = get_object_or_404(Producto, pk=pk, disponible=True)
    carrito = request.session.get('carrito', {})
    carrito[str(pk)] = min(carrito.get(str(pk), 0) + 1, 50)
    request.session['carrito'] = carrito
    messages.success(request, f'"{producto.nombre}" se agregó al carrito.')
    return redirect('productos')


@require_POST
def carrito_actualizar(request, pk):
    carrito = request.session.get('carrito', {})
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except ValueError:
        cantidad = 1
    if cantidad <= 0:
        carrito.pop(str(pk), None)
        messages.success(request, 'Producto quitado del carrito.')
    else:
        carrito[str(pk)] = min(cantidad, 50)
        messages.success(request, 'Carrito actualizado.')
    request.session['carrito'] = carrito
    return redirect('carrito')


@login_required
@require_POST
def carrito_confirmar(request):
    items, total = _items_carrito(request)
    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('productos')
    cliente, creado = Cliente.objects.get_or_create(
        user=request.user, defaults={'telefono': '', 'direccion': ''})
    with transaction.atomic():
        pedido = Pedido.objects.create(cliente=cliente, total=total)
        for it in items:
            DetallePedido.objects.create(
                pedido=pedido, producto=it['producto'],
                cantidad=it['cantidad'], precio_unitario=it['producto'].precio)
    request.session['carrito'] = {}
    messages.success(request, f'¡Pedido #{pedido.pk} registrado correctamente!')
    return redirect('mis_pedidos')

@login_required
def mis_pedidos(request):
    pedidos = (Pedido.objects.filter(cliente__user=request.user)
               .prefetch_related('detalles__producto'))
    return render(request, 'core/mis_pedidos.html', {'pedidos': pedidos})
