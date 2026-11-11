from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from .utils import normalizar


class TipoMenu(models.Model):
    """Entidad de contexto: clasifica los servicios (Cóctel, Almuerzo, Vegano, etc.)."""

    nombre = models.CharField('nombre', max_length=80, unique=True)
    descripcion = models.TextField('descripción', blank=True)
    activo = models.BooleanField('vigente', default=True)
    creado = models.DateTimeField('creado', auto_now_add=True)

    class Meta:
        verbose_name = 'tipo de menú'
        verbose_name_plural = 'tipos de menú'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ServicioCatering(models.Model):
    """Entidad principal gestionable: servicio que se cotiza por número de invitados."""

    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        AGOTADO = 'AGOTADO', 'Temporada agotada'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'

    # --- Relación referencial ---
    # PROTECT: impide borrar un TipoMenu que todavía tenga servicios asociados
    tipo_menu = models.ForeignKey(
        TipoMenu,
        on_delete=models.PROTECT,
        related_name='servicios',
        verbose_name='tipo de menú',
    )

    # --- Identificación ---
    codigo = models.CharField(
        'código', max_length=20, unique=True,
        help_text='Formato sugerido: CAT-001',
    )
    slug = models.SlugField('slug', max_length=120, unique=True, blank=True)

    # --- Atributos descriptivos ---
    nombre = models.CharField('nombre', max_length=120)
    descripcion = models.TextField('descripción')
    incluye = models.TextField(
        'incluye', blank=True,
        help_text='Detalle de lo que incluye el servicio (vajilla, garzones, montaje, etc.)',
    )

    # --- Atributos cuantitativos con validación ---
    precio_por_persona = models.PositiveIntegerField(
        'precio por persona (CLP)',
        validators=[MinValueValidator(1)],
    )
    minimo_invitados = models.PositiveIntegerField(
        'mínimo de invitados',
        default=10,
        validators=[MinValueValidator(1)],
    )
    maximo_invitados = models.PositiveIntegerField(
        'máximo de invitados (cupo)',
        default=200,
        validators=[MinValueValidator(1)],
    )

    # --- Estado operativo con opciones cerradas ---
    estado = models.CharField(
        'estado', max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )

    # --- Soporte multimedia ---
    imagen = models.ImageField('imagen', upload_to='servicios/', blank=True, null=True)

    # --- Baja lógica / vigencia ---
    activo = models.BooleanField('vigente', default=True)

    texto_busqueda = models.TextField(editable=False, blank=True)

    # --- Auditoría ---
    creado = models.DateTimeField('creado', auto_now_add=True)
    actualizado = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        verbose_name = 'servicio de catering'
        verbose_name_plural = 'servicios de catering'
        ordering = ['tipo_menu__nombre', 'nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    def clean(self):
        """Regla de negocio: el cupo máximo no puede ser menor al mínimo."""
        if (self.minimo_invitados and self.maximo_invitados
                and self.maximo_invitados < self.minimo_invitados):
            raise ValidationError({
                'maximo_invitados': 'El máximo de invitados no puede ser menor al mínimo.'
            })

        def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(f'{self.codigo}-{self.nombre}')
            self.texto_busqueda = normalizar(
                ' '.join([self.codigo, self.nombre, self.descripcion, self.incluye])
            )
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = {*kwargs['update_fields'], 'texto_busqueda'}
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catering:detalle', kwargs={'slug': self.slug})

    @property
    def esta_disponible(self):
        """Disponible para cotizar: vigente y en estado DISPONIBLE."""
        return self.activo and self.estado == self.Estado.DISPONIBLE