from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction

from catering.mixins import BootstrapFormMixin

from .models import Perfil
from .validators import validar_rut


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Formulario de inicio de sesión con estilos Bootstrap."""


class RegistroForm(BootstrapFormMixin, UserCreationForm):
    """Registro de usuario + datos del Perfil (RUT y teléfono) en un solo formulario."""

    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    rut = forms.CharField(
        label='RUT', max_length=10,
        validators=[validar_rut],
        help_text='Sin puntos y con guion. Ej: 12345678-5',
    )
    telefono = forms.CharField(
        label='Teléfono', max_length=12, required=False,
        validators=[RegexValidator(r'^\+569\d{8}$', 'Formato de teléfono: +56912345678')],
        help_text='Opcional. Formato: +56912345678',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    field_order = ['username', 'first_name', 'last_name', 'email', 'rut', 'telefono', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta registrada con este correo.')
        return email

    def clean_rut(self):
        rut = self.cleaned_data['rut'].strip().upper()
        if Perfil.objects.filter(rut__iexact=rut).exists():
            raise forms.ValidationError('Este RUT ya está registrado.')
        return rut

    @transaction.atomic
    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            # El Perfil ya lo creó la señal post_save; aquí se completan sus datos
            perfil = usuario.perfil
            perfil.rut = self.cleaned_data['rut']
            perfil.telefono = self.cleaned_data['telefono']
            perfil.rol = Perfil.Rol.CLIENTE
            perfil.save()
        return usuario
