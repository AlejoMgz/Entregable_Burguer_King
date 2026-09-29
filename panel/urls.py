from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='panel_dashboard'),
    path('pedidos/<int:pk>/', views.pedido_detalle, name='panel_pedido_detalle'),
    path('<slug:modulo>/', views.lista, name='panel_lista'),
    path('<slug:modulo>/nuevo/', views.crear, name='panel_crear'),
    path('<slug:modulo>/<int:pk>/editar/', views.editar, name='panel_editar'),
    path('<slug:modulo>/<int:pk>/eliminar/', views.eliminar, name='panel_eliminar'),
]