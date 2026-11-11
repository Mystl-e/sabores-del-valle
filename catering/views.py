from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import ServicioCatering, TipoMenu
from .utils import normalizar

# Opciones de ordenamiento permitidas (evita ordenar por cualquier campo que llegue por GET)
ORDENAMIENTOS = {
    'nombre': ('Nombre (A-Z)', 'nombre'),
    'precio_asc': ('Precio: menor a mayor', 'precio_por_persona'),
    'precio_desc': ('Precio: mayor a menor', '-precio_por_persona'),
    'recientes': ('Más recientes', '-creado'),
}


def catalogo(request):
    """R (Read): catálogo público con búsqueda multi-campo, filtro, orden y paginación."""
    # Solo servicios vigentes de tipos de menú vigentes; select_related evita N+1 consultas
    servicios = (
        ServicioCatering.objects
        .filter(activo=True, tipo_menu__activo=True)
        .select_related('tipo_menu')
    )

    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    orden = request.GET.get('orden', 'nombre')

    # Búsqueda simultánea en nombre, código y descripción con objetos Q (OR)
        # Búsqueda simultánea en nombre, código y descripción con objetos Q (OR).
    # texto_busqueda guarda esos campos sin tildes y en minúsculas: 'coctel' encuentra 'Cóctel'
    if q:
        servicios = servicios.filter(
            Q(nombre__icontains=q)
            | Q(codigo__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(texto_busqueda__contains=normalizar(q))
        )

    # Filtro por entidad de contexto
    if tipo.isdigit():
        servicios = servicios.filter(tipo_menu_id=int(tipo))

    if orden not in ORDENAMIENTOS:
        orden = 'nombre'
    servicios = servicios.order_by(ORDENAMIENTOS[orden][1])

    paginator = Paginator(servicios, 6)  # 6 tarjetas por página
    page_obj = paginator.get_page(request.GET.get('page'))

    contexto = {
        'page_obj': page_obj,
        'tipos': TipoMenu.objects.filter(activo=True),
        'ordenamientos': {clave: etiqueta for clave, (etiqueta, _) in ORDENAMIENTOS.items()},
        'q': q,
        'tipo_seleccionado': tipo,
        'orden': orden,
        'total': paginator.count,
    }
    return render(request, 'catering/catalogo.html', contexto)


def detalle(request, slug):
    """Ficha de detalle de un servicio, accesible por slug."""
    servicio = get_object_or_404(
        ServicioCatering.objects.select_related('tipo_menu'),
        slug=slug,
        activo=True,
    )
    return render(request, 'catering/detalle.html', {'servicio': servicio})
