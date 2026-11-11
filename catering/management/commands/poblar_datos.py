from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from catering.models import ServicioCatering, TipoMenu
from usuarios.models import Perfil

TIPOS_MENU = [
    {
        'nombre': 'Cóctel',
        'descripcion': 'Bocados fríos y calientes servidos por garzones, ideales para recepciones y lanzamientos.',
    },
    {
        'nombre': 'Almuerzo y Cena',
        'descripcion': 'Menús servidos a la mesa o en formato buffet para matrimonios y eventos formales.',
    },
    {
        'nombre': 'Vegano y Vegetariano',
        'descripcion': 'Preparaciones 100% vegetales o vegetarianas con productos de temporada.',
    },
    {
        'nombre': 'Repostería',
        'descripcion': 'Mesas dulces, tortas y postres individuales para cerrar el evento.',
    },
    {
        'nombre': 'Barra de Bebestibles',
        'descripcion': 'Barras atendidas de jugos, mocktails y café de especialidad.',
    },
]

SERVICIOS = [
    {
        'codigo': 'CAT-001', 'tipo': 'Cóctel',
        'nombre': 'Cóctel Clásico Chileno',
        'descripcion': 'Empanaditas de pino, sopaipillas con pebre, brochetas de pollo y mini choripanes.',
        'incluye': '12 bocados por persona, garzones y vajilla.',
        'precio_por_persona': 8900, 'minimo_invitados': 30, 'maximo_invitados': 300,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-002', 'tipo': 'Cóctel',
        'nombre': 'Cóctel Gourmet de Mar',
        'descripcion': 'Ceviche en cucharitas, machas a la parmesana, tártaro de salmón y camarones apanados.',
        'incluye': '14 bocados por persona, estación de mariscos y garzones.',
        'precio_por_persona': 14500, 'minimo_invitados': 30, 'maximo_invitados': 200,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-003', 'tipo': 'Almuerzo y Cena',
        'nombre': 'Asado Campestre',
        'descripcion': 'Parrilla de vacuno, cerdo y pollo con ensaladas chilenas, papas mayo y pebre.',
        'incluye': 'Parrillero, estación de ensaladas y pan amasado.',
        'precio_por_persona': 18900, 'minimo_invitados': 40, 'maximo_invitados': 250,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-004', 'tipo': 'Almuerzo y Cena',
        'nombre': 'Cena de Gala en Tres Tiempos',
        'descripcion': 'Entrada, plato de fondo a elección (filete o salmón) y postre emplatado.',
        'incluye': 'Servicio a la mesa, mantelería, cristalería y montaje.',
        'precio_por_persona': 32000, 'minimo_invitados': 50, 'maximo_invitados': 300,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-005', 'tipo': 'Vegano y Vegetariano',
        'nombre': 'Buffet Vegano de Temporada',
        'descripcion': 'Lasaña de verduras, curry de garbanzos, quinoa con vegetales asados y ensaladas.',
        'incluye': 'Montaje de buffet y reposición durante 2 horas.',
        'precio_por_persona': 15900, 'minimo_invitados': 20, 'maximo_invitados': 150,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-006', 'tipo': 'Vegano y Vegetariano',
        'nombre': 'Cóctel Vegetariano Mediterráneo',
        'descripcion': 'Falafel, hummus con crudités, bruschettas y brochetas caprese.',
        'incluye': '10 bocados por persona y garzones.',
        'precio_por_persona': 11500, 'minimo_invitados': 25, 'maximo_invitados': 180,
        'estado': ServicioCatering.Estado.AGOTADO,
    },
    {
        'codigo': 'CAT-007', 'tipo': 'Repostería',
        'nombre': 'Mesa Dulce Tradicional',
        'descripcion': 'Alfajores, chilenitos, kuchen de frutas, brazo de reina y mini cheesecakes.',
        'incluye': 'Montaje decorado y 6 piezas por persona.',
        'precio_por_persona': 6500, 'minimo_invitados': 30, 'maximo_invitados': 300,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-008', 'tipo': 'Repostería',
        'nombre': 'Torta de Novios Personalizada',
        'descripcion': 'Torta de pisos con diseño a pedido: hojarasca manjar, tres leches o selva negra.',
        'incluye': 'Diseño, degustación previa y servicio de corte.',
        'precio_por_persona': 4900, 'minimo_invitados': 50, 'maximo_invitados': 400,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-009', 'tipo': 'Barra de Bebestibles',
        'nombre': 'Barra de Jugos Naturales y Mocktails',
        'descripcion': 'Jugos naturales de temporada, limonadas y cócteles sin alcohol.',
        'incluye': 'Bartender por 3 horas, hielo y cristalería.',
        'precio_por_persona': 4500, 'minimo_invitados': 20, 'maximo_invitados': 300,
        'estado': ServicioCatering.Estado.DISPONIBLE,
    },
    {
        'codigo': 'CAT-010', 'tipo': 'Barra de Bebestibles',
        'nombre': 'Barra de Café de Especialidad',
        'descripcion': 'Espresso, capuccino y métodos de filtrado con granos de tostaduría local.',
        'incluye': 'Barista por 3 horas y máquina profesional.',
        'precio_por_persona': 3900, 'minimo_invitados': 20, 'maximo_invitados': 200,
        'estado': ServicioCatering.Estado.SUSPENDIDO,
    },
]

USUARIOS = [
    {
        'username': 'admin', 'password': 'Admin.2026',
        'email': 'admin@saboresdelvalle.cl', 'first_name': 'Ana', 'last_name': 'Administradora',
        'is_staff': True, 'is_superuser': True,
        'perfil': {'rut': '11111111-1', 'telefono': '+56911111111', 'rol': Perfil.Rol.ADMINISTRADOR},
    },
    {
        'username': 'coordinador', 'password': 'Coord.2026',
        'email': 'coordinacion@saboresdelvalle.cl', 'first_name': 'Carlos', 'last_name': 'Coordinador',
        'is_staff': True, 'is_superuser': False,
        'perfil': {'rut': '22222222-2', 'telefono': '+56922222222', 'rol': Perfil.Rol.COORDINADOR},
    },
    {
        'username': 'cliente', 'password': 'Cliente.2026',
        'email': 'cliente@correo.cl', 'first_name': 'Camila', 'last_name': 'Cliente',
        'is_staff': False, 'is_superuser': False,
        'perfil': {'rut': '12345678-5', 'telefono': '+56933333333', 'rol': Perfil.Rol.CLIENTE},
    },
]


class Command(BaseCommand):
    help = 'Carga tipos de menú, servicios de catering y usuarios de prueba (admin, coordinador y cliente).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Elimina todos los servicios y tipos de menú antes de cargar.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            # Primero los servicios: el PROTECT impide borrar tipos de menú con servicios asociados
            n_serv, _ = ServicioCatering.objects.all().delete()
            n_tipo, _ = TipoMenu.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f'Reset: eliminados {n_serv} servicios y {n_tipo} tipos de menú.'
            ))

        # --- Tipos de menú (entidad de contexto) ---
        tipos = {}
        for datos in TIPOS_MENU:
            tipo, creado = TipoMenu.objects.update_or_create(
                nombre=datos['nombre'],
                defaults={'descripcion': datos['descripcion'], 'activo': True},
            )
            tipos[tipo.nombre] = tipo
            self._informar('Tipo de menú', tipo, creado)

        # --- Servicios de catering (entidad principal) ---
        for datos in SERVICIOS:
            datos = datos.copy()
            codigo = datos.pop('codigo')
            datos['tipo_menu'] = tipos[datos.pop('tipo')]
            datos.setdefault('activo', True)
            servicio, creado = ServicioCatering.objects.update_or_create(codigo=codigo, defaults=datos)
            self._informar('Servicio', servicio, creado)

        # --- Usuarios de prueba con su perfil ---
        User = get_user_model()
        for datos in USUARIOS:
            datos = datos.copy()
            password = datos.pop('password')
            datos_perfil = datos.pop('perfil')
            username = datos.pop('username')

            usuario, creado = User.objects.update_or_create(username=username, defaults=datos)
            usuario.set_password(password)  # siempre deja la contraseña documentada en el README
            usuario.save()

            Perfil.objects.update_or_create(usuario=usuario, defaults=datos_perfil)
            self._informar('Usuario', usuario, creado)

        # Usuarios creados antes de existir el modelo Perfil (ej. tu primer superusuario)
        for usuario in User.objects.filter(perfil__isnull=True):
            Perfil.objects.create(usuario=usuario)
            self.stdout.write(f'  Perfil creado para usuario existente: {usuario.username}')

        self.stdout.write(self.style.SUCCESS(
            f'\nCarga completa: {TipoMenu.objects.count()} tipos de menú, '
            f'{ServicioCatering.objects.count()} servicios y {User.objects.count()} usuarios.'
        ))

    def _informar(self, entidad, objeto, creado):
        accion = 'creado' if creado else 'actualizado'
        self.stdout.write(f'  {entidad} {accion}: {objeto}')
