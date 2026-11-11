"""
Backoffice (CRUD en frontend). Todas las vistas exigen:
  1) @login_required        -> usuario autenticado (si no, redirige al login)
  2) @user_passes_test       -> usuario staff (si no, error 403 Prohibido)
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ServicioCateringForm
from .models import ServicioCatering
from .utils import normalizar


def es_staff(usuario):
    """Permite el paso solo a personal (is_staff). Un usuario común recibe 403."""
    if usuario.is_authenticated and not usuario.is_staff:
        raise PermissionDenied
    return usuario.is_staff


@login_required
@user_passes_test(es_staff)
def gestion_lista(request):
    """Listado de gestión: incluye servicios dados de baja, con búsqueda y filtro de vigencia."""
    servicios = ServicioCatering.objects.select_related('tipo_menu').order_by('codigo')

    q = request.GET.get('q', '').strip()
    vigencia = request.GET.get('vigencia', '')

    if q:
        servicios = servicios.filter(
            Q(nombre__icontains=q)
            | Q(codigo__icontains=q)
            | Q(texto_busqueda__contains=normalizar(q))
        )
    if vigencia == 'activos':
        servicios = servicios.filter(activo=True)
    elif vigencia == 'baja':
        servicios = servicios.filter(activo=False)

    page_obj = Paginator(servicios, 10).get_page(request.GET.get('page'))
    return render(request, 'catering/gestion/lista.html', {
        'page_obj': page_obj, 'q': q, 'vigencia': vigencia,
    })


@login_required
@user_passes_test(es_staff)
def servicio_crear(request):
    """C (Create): ModelForm + archivos (request.FILES)."""
    if request.method == 'POST':
        form = ServicioCateringForm(request.POST, request.FILES)
        if form.is_valid():
            servicio = form.save()
            messages.success(request, f'Servicio "{servicio}" creado correctamente.')
            return redirect('catering:gestion')
        messages.error(request, 'No se pudo crear el servicio. Revisa los campos marcados.')
    else:
        form = ServicioCateringForm()

    return render(request, 'catering/gestion/form.html', {'form': form, 'titulo': 'Nuevo servicio'})


@login_required
@user_passes_test(es_staff)
def servicio_editar(request, pk):
    """U (Update): mismo formulario precargado con la instancia existente."""
    servicio = get_object_or_404(ServicioCatering, pk=pk)

    if request.method == 'POST':
        form = ServicioCateringForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, f'Servicio "{servicio}" actualizado correctamente.')
            return redirect('catering:gestion')
        messages.error(request, 'No se pudieron guardar los cambios. Revisa los campos marcados.')
    else:
        form = ServicioCateringForm(instance=servicio)

    return render(request, 'catering/gestion/form.html', {
        'form': form, 'servicio': servicio, 'titulo': f'Editar {servicio.codigo}',
    })


@login_required
@user_passes_test(es_staff)
def servicio_baja(request, pk):
    """D (Delete): baja lógica con pantalla de confirmación previa (GET confirma, POST ejecuta)."""
    servicio = get_object_or_404(ServicioCatering, pk=pk, activo=True)

    if request.method == 'POST':
        servicio.activo = False
        servicio.save(update_fields=['activo', 'actualizado'])
        messages.warning(request, f'Servicio "{servicio}" dado de baja. Ya no aparece en el catálogo público.')
        return redirect('catering:gestion')

    return render(request, 'catering/gestion/confirmar_baja.html', {'servicio': servicio})


@login_required
@user_passes_test(es_staff)
@require_POST
def servicio_reactivar(request, pk):
    """Revierte la baja lógica."""
    servicio = get_object_or_404(ServicioCatering, pk=pk, activo=False)
    servicio.activo = True
    servicio.save(update_fields=['activo', 'actualizado'])
    messages.success(request, f'Servicio "{servicio}" reactivado.')
    return redirect('catering:gestion')
