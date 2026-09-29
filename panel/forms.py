from django import forms
from django.contrib.auth.models import User

from core.forms import BootstrapMixin
from core.models import (Categoria, Producto, Servicio, Slide,
                         Cliente, Pedido, Mensaje)


def crear_form(modelo, campos):
    meta = type('Meta', (), {'model': modelo, 'fields': campos})
    return type(f'{modelo.__name__}Form', (BootstrapMixin, forms.ModelForm), {'Meta': meta})


CategoriaForm = crear_form(Categoria, ['nombre', 'descripcion', 'activa'])
ProductoForm = crear_form(Producto, ['categoria', 'nombre', 'descripcion', 'precio',
                                     'imagen', 'disponible', 'destacado'])
ServicioForm = crear_form(Servicio, ['nombre', 'descripcion', 'imagen', 'activo'])
SlideForm = crear_form(Slide, ['titulo', 'subtitulo', 'imagen', 'orden', 'activo'])
PedidoForm = crear_form(Pedido, ['cliente', 'estado', 'total'])
MensajeForm = crear_form(Mensaje, ['nombre', 'email', 'asunto', 'mensaje', 'leido'])


class ClientePanelForm(BootstrapMixin, forms.ModelForm):
    username = forms.CharField(label='Usuario', max_length=150)
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(label='Correo')
    password = forms.CharField(
        label='Contraseña', required=False, widget=forms.PasswordInput(render_value=False),
        help_text='Obligatoria al crear. Al editar, déjala vacía para no cambiarla.')

    class Meta:
        model = Cliente
        fields = ['telefono', 'direccion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            u = self.instance.user
            self.fields['username'].initial = u.username
            self.fields['first_name'].initial = u.first_name
            self.fields['last_name'].initial = u.last_name
            self.fields['email'].initial = u.email

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError('Ese usuario ya existe.')
        return username

    def clean(self):
        datos = super().clean()
        if not self.instance.pk and not datos.get('password'):
            self.add_error('password', 'La contraseña es obligatoria al crear un cliente.')
        return datos

    def save(self, commit=True):
        d = self.cleaned_data
        user = self.instance.user if self.instance.pk else User()
        user.username = d['username']
        user.first_name = d['first_name']
        user.last_name = d['last_name']
        user.email = d['email']
        if d.get('password'):
            user.set_password(d['password'])
        user.save()
        cliente = super().save(commit=False)
        cliente.user = user
        if commit:
            cliente.save()
        return cliente