import secrets

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .cotizacion import TASA_IVA, TASA_SERVICIO, Cotizacion
from .models import ServicioCatering


class InvitadosForm(forms.Form):
    """Valida que la cantidad de invitados sea un entero positivo."""
    invitados = forms.IntegerField(min_value=1, max_value=5000)


def _leer_invitados(request):
    form = InvitadosForm(request.POST)
    if form.is_valid():
        return form.cleaned_data['invitados']
    return None


@require_POST
def agregar(request, pk):
    """Agrega un servicio a la cotización (o actualiza sus invitados si ya estaba)."""
    servicio = get_object_or_404(ServicioCatering, pk=pk, activo=True)
    invitados = _leer_invitados(request)
    if invitados is None:
        messages.error(request, 'Ingresa una cantidad de invitados válida.')
        return redirect(servicio.get_absolute_url())

    cotizacion = Cotizacion(request)
    ya_estaba = pk in cotizacion
    error = cotizacion.agregar(servicio, invitados)
    if error:
        messages.error(request, error)
        return redirect(servicio.get_absolute_url())

    accion = 'actualizado en' if ya_estaba else 'agregado a'
    messages.success(request, f'"{servicio.nombre}" {accion} tu cotización ({invitados} invitados).')
    return redirect('catering:cotizacion')


@require_POST
def actualizar(request, pk):
    """Modifica la cantidad de invitados de un servicio ya agregado."""
    cotizacion = Cotizacion(request)
    if pk not in cotizacion:
        messages.error(request, 'Ese servicio no está en tu cotización.')
        return redirect('catering:cotizacion')

    servicio = get_object_or_404(ServicioCatering, pk=pk)
    invitados = _leer_invitados(request)
    if invitados is None:
        messages.error(request, 'Ingresa una cantidad de invitados válida.')
    else:
        error = cotizacion.agregar(servicio, invitados)
        if error:
            messages.error(request, error)
        else:
            messages.success(request, f'Invitados de "{servicio.nombre}" actualizados a {invitados}.')
    return redirect('catering:cotizacion')


@require_POST
def eliminar(request, pk):
    Cotizacion(request).eliminar(pk)
    messages.info(request, 'Servicio quitado de la cotización.')
    return redirect('catering:cotizacion')


@require_POST
def vaciar(request):
    Cotizacion(request).vaciar()
    messages.info(request, 'Cotización vaciada.')
    return redirect('catering:cotizacion')


def ver_cotizacion(request):
    """Muestra la colección en sesión con el desglose económico."""
    cotizacion = Cotizacion(request)
    for nombre in cotizacion.quitar_no_disponibles():
        messages.warning(request, f'"{nombre}" ya no está disponible y se quitó de tu cotización.')

    lineas = cotizacion.lineas()
    return render(request, 'catering/cotizacion.html', {
        'lineas': lineas,
        'totales': Cotizacion.totales(lineas),
        'tasa_servicio': int(TASA_SERVICIO * 100),
        'tasa_iva': int(TASA_IVA * 100),
    })


@login_required
@require_POST
def confirmar(request):
    """Genera la solicitud simulada (comprobante) y vacía la sesión."""
    cotizacion = Cotizacion(request)
    quitados = cotizacion.quitar_no_disponibles()
    lineas = cotizacion.lineas()
    if quitados or not lineas:
        messages.error(request, 'Revisa tu cotización antes de confirmarla.')
        return redirect('catering:cotizacion')

    ahora = timezone.localtime()
    comprobante = {
        'folio': f'SV-{ahora:%Y%m%d}-{secrets.token_hex(2).upper()}',
        'fecha': ahora.strftime('%d-%m-%Y %H:%M'),
        'cliente': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'lineas': [
            {
                'codigo': l['servicio'].codigo,
                'nombre': l['servicio'].nombre,
                'precio': l['servicio'].precio_por_persona,
                'invitados': l['invitados'],
                'subtotal': l['subtotal'],
            }
            for l in lineas
        ],
        'totales': Cotizacion.totales(lineas),
    }

    cotizacion.vaciar()
    request.session['ultimo_comprobante'] = comprobante
    messages.success(request, f'Solicitud {comprobante["folio"]} generada correctamente.')
    return redirect('catering:comprobante')


@login_required
def comprobante(request):
    datos = request.session.get('ultimo_comprobante')
    if not datos:
        messages.info(request, 'Aún no has generado ninguna solicitud.')
        return redirect('catering:catalogo')
    return render(request, 'catering/comprobante.html', {
        'c': datos,
        'tasa_servicio': int(TASA_SERVICIO * 100),
        'tasa_iva': int(TASA_IVA * 100),
    })
