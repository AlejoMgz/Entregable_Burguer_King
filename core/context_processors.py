def carrito_contador(request):
    carrito = request.session.get('carrito', {})
    return {'carrito_total_items': sum(carrito.values())}