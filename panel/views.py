from django.shortcuts import render
from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db.models import ProtectedError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from core.models import (Categoria, Producto, Servicio, Slide,
                         Cliente, Pedido, Mensaje)
from .forms import (CategoriaForm, ProductoForm, ServicioForm, SlideForm,
                    ClientePanelForm, PedidoForm, MensajeForm)


def staff_required(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), 'login')
        if not request.user.is_staff:
            messages.error(request, 'No tienes permisos para entrar al panel administrativo.')
            return redirect('home')
        return vista(request, *args, **kwargs)
    return envoltura


MODULOS = {
    'categorias': dict(modelo=Categoria, form=CategoriaForm, titulo='Categorías',
                       singular='Categoría', icono='bi-tags',
                       columnas=[('nombre', 'Nombre'), ('descripcion', 'Descripción'),
                                 ('activa', 'Activa')]),
    'productos': dict(modelo=Producto, form=ProductoForm, titulo='Productos',
                      singular='Producto', icono='bi-basket',
                      columnas=[('imagen', 'Imagen'), ('nombre', 'Nombre'),
                                ('categoria', 'Categoría'), ('precio', 'Precio'),
                                ('disponible', 'Disponible'), ('destacado', 'Destacado')]),
    'servicios': dict(modelo=Servicio, form=ServicioForm, titulo='Servicios',
                      singular='Servicio', icono='bi-truck',
                      columnas=[('imagen', 'Imagen'), ('nombre', 'Nombre'),
                                ('activo', 'Activo')]),
    'slides': dict(modelo=Slide, form=SlideForm, titulo='Slider del Home',
                   singular='Slide', icono='bi-images',
                   columnas=[('imagen', 'Imagen'), ('titulo', 'Título'),
                             ('orden', 'Orden'), ('activo', 'Activo')]),
    'clientes': dict(modelo=Cliente, form=ClientePanelForm, titulo='Clientes',
                     singular='Cliente', icono='bi-people',
                     columnas=[('user', 'Usuario'), ('telefono', 'Teléfono'),
                               ('direccion', 'Dirección')]),
    'pedidos': dict(modelo=Pedido, form=PedidoForm, titulo='Pedidos',
                    singular='Pedido', icono='bi-receipt',
                    columnas=[('id', 'N°'), ('cliente', 'Cliente'), ('fecha', 'Fecha'),
                              ('estado', 'Estado'), ('total', 'Total')]),
    'mensajes': dict(modelo=Mensaje, form=MensajeForm, titulo='Mensajes de contacto',
                     singular='Mensaje', icono='bi-envelope',
                     columnas=[('fecha', 'Fecha'), ('nombre', 'Nombre'),
                               ('email', 'Correo'), ('asunto', 'Asunto'),
                               ('leido', 'Leído')]),
}


def _cfg(modulo):
    if modulo not in MODULOS:
        raise Http404
    return MODULOS[modulo]


def _ctx(activo=None, **extra):
    return {'menu': MODULOS, 'activo': activo, **extra}


def _celda(obj, attr):
    valor = getattr(obj, attr)
    if attr == 'imagen':
        return {'tipo': 'img', 'v': valor.url if valor else ''}
    if isinstance(valor, bool):
        return {'tipo': 'bool', 'v': valor}
    display = getattr(obj, f'get_{attr}_display', None)
    if display:
        valor = display()
    return {'tipo': 'txt', 'v': valor}


@staff_required
def dashboard(request):
    tarjetas = [{'slug': s, 'titulo': m['titulo'], 'icono': m['icono'],
                 'total': m['modelo'].objects.count()} for s, m in MODULOS.items()]
    return render(request, 'panel/dashboard.html', _ctx(tarjetas=tarjetas))


@staff_required
def lista(request, modulo):
    cfg = _cfg(modulo)
    filas = [{'obj': o, 'celdas': [_celda(o, attr) for attr, _ in cfg['columnas']]}
             for o in cfg['modelo'].objects.all()]
    return render(request, 'panel/lista.html', _ctx(modulo, cfg=cfg, filas=filas, modulo=modulo))


@staff_required
def crear(request, modulo):
    cfg = _cfg(modulo)
    form = cfg['form'](request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'{cfg["singular"]} guardado correctamente.')
            return redirect('panel_lista', modulo=modulo)
        messages.error(request, 'No se pudo guardar. Revisa los errores del formulario.')
    return render(request, 'panel/form.html',
                  _ctx(modulo, form=form, titulo=f'Nuevo {cfg["singular"].lower()}', modulo=modulo))


@staff_required
def editar(request, modulo, pk):
    cfg = _cfg(modulo)
    obj = get_object_or_404(cfg['modelo'], pk=pk)
    form = cfg['form'](request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'{cfg["singular"]} actualizado correctamente.')
            return redirect('panel_lista', modulo=modulo)
        messages.error(request, 'No se pudo actualizar. Revisa los errores del formulario.')
    return render(request, 'panel/form.html',
                  _ctx(modulo, form=form, titulo=f'Editar {cfg["singular"].lower()}', modulo=modulo))


@staff_required
def eliminar(request, modulo, pk):
    cfg = _cfg(modulo)
    obj = get_object_or_404(cfg['modelo'], pk=pk)
    if request.method == 'POST':
        objetivo = obj.user if modulo == 'clientes' else obj
        try:
            objetivo.delete()
            messages.success(request, f'{cfg["singular"]} eliminado correctamente.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: tiene registros relacionados '
                                    '(por ejemplo, productos o pedidos).')
        return redirect('panel_lista', modulo=modulo)
    return render(request, 'panel/eliminar.html',
                  _ctx(modulo, obj=obj, cfg=cfg, modulo=modulo))


@staff_required
def pedido_detalle(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    return render(request, 'panel/pedido_detalle.html',
                  _ctx('pedidos', pedido=pedido, detalles=pedido.detalles.select_related('producto')))