def cotizacion(request):
    """Inyecta en TODAS las plantillas la cantidad de servicios en la cotización (sesión)."""
    items = request.session.get('cotizacion', {})
    return {'cotizacion_cantidad': len(items)}
