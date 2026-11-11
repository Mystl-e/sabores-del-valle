from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .validators import validar_rut


class Perfil(models.Model):

    class Rol(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        COORDINADOR = 'COORDINADOR', 'Coordinador de eventos'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='usuario',
    )
    # null=True permite varios perfiles sin RUT sin romper la restricción unique
    rut = models.CharField(
        'RUT', max_length=10, unique=True, null=True, blank=True,
        validators=[validar_rut],
        help_text='Sin puntos y con guion. Ej: 12345678-5',
    )
    telefono = models.CharField(
        'teléfono', max_length=12, blank=True,
        validators=[RegexValidator(r'^\+569\d{8}$', 'Formato de teléfono: +56912345678')],
    )
    rol = models.CharField(
        'rol institucional', max_length=20,
        choices=Rol.choices, default=Rol.CLIENTE,
    )

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return f'Perfil de {self.usuario.username} ({self.get_rol_display()})'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente el Perfil cada vez que se registra un usuario nuevo."""
    if created:
        Perfil.objects.get_or_create(usuario=instance)