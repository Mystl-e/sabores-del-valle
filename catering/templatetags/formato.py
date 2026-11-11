from django import template

register = template.Library()


@register.filter
def clp(valor):
    """Formatea un número como pesos chilenos: 18900 -> $18.900"""
    try:
        return '$' + f'{int(valor):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return valor


@register.filter
def color_estado(estado):
    """Clase de color Bootstrap según el estado del servicio."""
    return {
        'DISPONIBLE': 'success',
        'AGOTADO': 'warning',
        'SUSPENDIDO': 'secondary',
    }.get(estado, 'light')
