import re

from django import forms

from .mixins import BootstrapFormMixin
from .models import ServicioCatering, TipoMenu

TAMANO_MAXIMO_IMAGEN_MB = 2


class ServicioCateringForm(BootstrapFormMixin, forms.ModelForm):
    """C y U: formulario de creación/edición de servicios con validaciones clean_()."""

    class Meta:
        model = ServicioCatering
        fields = [
            'tipo_menu', 'codigo', 'nombre', 'descripcion', 'incluye',
            'precio_por_persona', 'minimo_invitados', 'maximo_invitados',
            'estado', 'imagen', 'activo',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'incluye': forms.Textarea(attrs={'rows': 2}),
            'codigo': forms.TextInput(attrs={'placeholder': 'CAT-011'}),
            'precio_por_persona': forms.NumberInput(attrs={'min': 1}),
            'minimo_invitados': forms.NumberInput(attrs={'min': 1}),
            'maximo_invitados': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se pueden asignar tipos de menú vigentes
        self.fields['tipo_menu'].queryset = TipoMenu.objects.filter(activo=True)

    def clean_codigo(self):
        """Identificador: formato AAA-000 y único (excluyendo el propio registro al editar)."""
        codigo = self.cleaned_data['codigo'].strip().upper()
        if not re.fullmatch(r'[A-Z]{3}-\d{3}', codigo):
            raise forms.ValidationError('El código debe tener el formato AAA-000 (ej: CAT-011).')
        existe = ServicioCatering.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists()
        if existe:
            raise forms.ValidationError(f'Ya existe un servicio con el código {codigo}.')
        return codigo

    def clean_precio_por_persona(self):
        precio = self.cleaned_data['precio_por_persona']
        if precio is None or precio <= 0:
            raise forms.ValidationError('El precio por persona debe ser mayor a 0.')
        return precio

    def clean_minimo_invitados(self):
        minimo = self.cleaned_data['minimo_invitados']
        if minimo is None or minimo < 1:
            raise forms.ValidationError('El mínimo de invitados debe ser al menos 1.')
        return minimo

    def clean_maximo_invitados(self):
        maximo = self.cleaned_data['maximo_invitados']
        if maximo is None or maximo < 1:
            raise forms.ValidationError('El máximo de invitados debe ser al menos 1.')
        return maximo

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen and hasattr(imagen, 'size') and imagen.size > TAMANO_MAXIMO_IMAGEN_MB * 1024 * 1024:
            raise forms.ValidationError(f'La imagen no puede superar los {TAMANO_MAXIMO_IMAGEN_MB} MB.')
        return imagen

    def clean(self):
        """Validación cruzada: el máximo de invitados no puede ser menor al mínimo."""
        datos = super().clean()
        minimo = datos.get('minimo_invitados')
        maximo = datos.get('maximo_invitados')
        if minimo and maximo and maximo < minimo:
            self.add_error('maximo_invitados', 'El máximo de invitados no puede ser menor al mínimo.')
        return datos
