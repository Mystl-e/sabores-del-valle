from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html

from .models import ServicioCatering, TipoMenu

# --- Identidad corporativa del panel ---
admin.site.site_header = 'Sabores del Valle Banquetería - Panel de Control'
admin.site.site_title = 'Sabores del Valle Admin'
admin.site.index_title = 'Gestión Operativa de Recursos y Servicios'


class ServicioCateringInline(admin.TabularInline):
    """Muestra (solo lectura) los servicios asociados dentro de cada TipoMenu."""
    model = ServicioCatering
    fields = ('codigo', 'nombre', 'precio_por_persona', 'estado', 'activo')
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TipoMenu)
class TipoMenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_servicios', 'activo', 'creado')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)
    inlines = [ServicioCateringInline]

    def get_queryset(self, request):
        # Cuenta los servicios en la misma consulta (evita una query por fila)
        return super().get_queryset(request).annotate(_cantidad=Count('servicios'))

    @admin.display(description='N° de servicios', ordering='_cantidad')
    def cantidad_servicios(self, obj):
        return obj._cantidad


@admin.register(ServicioCatering)
class ServicioCateringAdmin(admin.ModelAdmin):
    # Vista tabular: identificador, nombre, contexto, valores, estado y vigencia
    list_display = (
        'codigo', 'nombre', 'tipo_menu', 'precio_por_persona',
        'minimo_invitados', 'estado', 'activo',
    )
    list_display_links = ('codigo', 'nombre')
    list_filter = ('tipo_menu', 'estado', 'activo')
    search_fields = ('codigo', 'nombre', 'descripcion', 'tipo_menu__nombre')
    list_editable = ('precio_por_persona', 'estado', 'activo')
    list_select_related = ('tipo_menu',)  # JOIN con TipoMenu: evita el problema N+1
    list_per_page = 20
    ordering = ('codigo',)
    prepopulated_fields = {'slug': ('codigo', 'nombre')}
    readonly_fields = ('vista_previa', 'creado', 'actualizado')
    actions = ('dar_de_baja', 'reactivar')

    # Formulario dividido en secciones temáticas
    fieldsets = (
        ('Identificación', {
            'fields': ('tipo_menu', 'codigo', 'slug', 'nombre'),
        }),
        ('Descripción y multimedia', {
            'fields': ('descripcion', 'incluye', 'imagen', 'vista_previa'),
        }),
        ('Precios y cupos', {
            'fields': ('precio_por_persona', 'minimo_invitados', 'maximo_invitados'),
            'description': 'Valores en pesos chilenos (CLP). El máximo no puede ser menor al mínimo.',
        }),
        ('Estado y vigencia', {
            'fields': ('estado', 'activo'),
        }),
        ('Auditoría', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Vista previa')
    def vista_previa(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-height:150px;border-radius:6px;">',
                obj.imagen.url,
            )
        return 'Sin imagen'

    # --- Acciones masivas de baja lógica ---
    @admin.action(description='Dar de baja (desactivar) servicios seleccionados')
    def dar_de_baja(self, request, queryset):
        n = queryset.update(activo=False)
        self.message_user(request, f'{n} servicio(s) dado(s) de baja.', messages.SUCCESS)

    @admin.action(description='Reactivar servicios seleccionados')
    def reactivar(self, request, queryset):
        n = queryset.update(activo=True)
        self.message_user(request, f'{n} servicio(s) reactivado(s).', messages.SUCCESS)