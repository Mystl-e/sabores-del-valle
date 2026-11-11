"""
Cotizador de evento guardado en request.session (sin persistir en la base de datos).

Estructura en la sesión:
    request.session['cotizacion'] = {
        '<id del servicio>': {'invitados': 40},
        ...
    }
Solo se guarda el id y la cantidad de invitados: los precios se leen siempre
desde la base de datos, así nadie puede alterarlos desde el navegador.
"""
from decimal import ROUND_HALF_UP, Decimal

from .models import ServicioCatering

CLAVE_SESION = 'cotizacion'
TASA_SERVICIO = Decimal('0.10')  # 10% cargo por servicio de garzones
TASA_IVA = Decimal('0.19')       # IVA Chile 19%


def redondear_clp(valor):
    """Redondea a pesos enteros (los CLP no usan decimales)."""
    return int(Decimal(valor).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def validar_invitados(servicio, invitados):
    """Regla de negocio: disponibilidad + rango [mínimo, máximo] de invitados. Devuelve error o None."""
    if not servicio.esta_disponible:
        return f'"{servicio.nombre}" no está disponible para cotizar ({servicio.get_estado_display()}).'
    if invitados < servicio.minimo_invitados:
        return f'"{servicio.nombre}" requiere un mínimo de {servicio.minimo_invitados} invitados.'
    if invitados > servicio.maximo_invitados:
        return f'"{servicio.nombre}" tiene un cupo máximo de {servicio.maximo_invitados} invitados.'
    return None


class Cotizacion:
    """Envoltorio de la colección en sesión con sus operaciones y cálculos."""

    def __init__(self, request):
        self.session = request.session
        self.items = self.session.get(CLAVE_SESION, {})

    def __len__(self):
        return len(self.items)

    def __contains__(self, servicio_id):
        return str(servicio_id) in self.items

    def invitados_de(self, servicio_id):
        item = self.items.get(str(servicio_id))
        return item['invitados'] if item else None

    def _guardar(self):
        self.session[CLAVE_SESION] = self.items
        self.session.modified = True  # obliga a Django a guardar el diccionario modificado

    # ---------- Operaciones ----------
    def agregar(self, servicio, invitados):
        """Agrega el servicio o, si ya estaba, reemplaza su cantidad de invitados."""
        error = validar_invitados(servicio, invitados)
        if error:
            return error
        self.items[str(servicio.pk)] = {'invitados': invitados}
        self._guardar()
        return None

    def eliminar(self, servicio_id):
        if self.items.pop(str(servicio_id), None) is not None:
            self._guardar()

    def vaciar(self):
        self.items = {}
        self.session.pop(CLAVE_SESION, None)
        self.session.modified = True

    def quitar_no_disponibles(self):
        """Saca servicios que se dieron de baja o cambiaron de estado mientras estaban en la sesión."""
        servicios = ServicioCatering.objects.in_bulk([int(pk) for pk in self.items])
        quitados = []
        for pk in list(self.items):
            servicio = servicios.get(int(pk))
            if servicio is None or not servicio.esta_disponible:
                quitados.append(servicio.nombre if servicio else f'Servicio #{pk}')
                del self.items[pk]
        if quitados:
            self._guardar()
        return quitados

    # ---------- Cálculos ----------
    def lineas(self):
        """Detalle por servicio: precio, invitados y subtotal (una sola consulta con select_related)."""
        servicios = (
            ServicioCatering.objects
            .filter(pk__in=[int(pk) for pk in self.items])
            .select_related('tipo_menu')
            .order_by('tipo_menu__nombre', 'nombre')
        )
        resultado = []
        for servicio in servicios:
            invitados = self.items[str(servicio.pk)]['invitados']
            resultado.append({
                'servicio': servicio,
                'invitados': invitados,
                'subtotal': servicio.precio_por_persona * invitados,
            })
        return resultado

    @staticmethod
    def totales(lineas):
        """Subtotal + 10% servicio = neto; IVA 19% sobre el neto; total final."""
        subtotal = sum(linea['subtotal'] for linea in lineas)
        cargo_servicio = redondear_clp(subtotal * TASA_SERVICIO)
        neto = subtotal + cargo_servicio
        iva = redondear_clp(neto * TASA_IVA)
        return {
            'subtotal': subtotal,
            'cargo_servicio': cargo_servicio,
            'neto': neto,
            'iva': iva,
            'total': neto + iva,
        }
