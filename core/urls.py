urlpatterns = []
from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('servicios/', views.servicios, name='servicios'),
    path('productos/', views.productos, name='productos'),
    path('contacto/', views.contacto, name='contacto'),
    path('ingresar/', views.LoginPersonalizado.as_view(), name='login'),
    path('salir/', LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:pk>/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/actualizar/<int:pk>/', views.carrito_actualizar, name='carrito_actualizar'),
    path('carrito/confirmar/', views.carrito_confirmar, name='carrito_confirmar'),
]