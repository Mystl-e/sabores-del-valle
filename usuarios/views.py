from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm


def registro(request):
    """Crea la cuenta (usuario + perfil) e inicia sesión automáticamente."""
    if request.user.is_authenticated:
        return redirect('catering:catalogo')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a, {usuario.first_name}! Tu cuenta fue creada.')
            return redirect('catering:catalogo')
        messages.error(request, 'Revisa los datos marcados en el formulario.')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


class IngresoView(SuccessMessageMixin, LoginView):
    """Login con plantilla propia; si ya hay sesión iniciada redirige al catálogo."""
    template_name = 'usuarios/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_message(self, cleaned_data):
        usuario = self.request.user
        return f'Hola, {usuario.first_name or usuario.username}. Sesión iniciada.'


@require_POST  # el logout solo por POST (con CSRF) evita cierres de sesión por enlaces maliciosos
def salir(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('catering:catalogo')


@login_required
def perfil(request):
    """Muestra los datos de la cuenta y del perfil del usuario conectado."""
    return render(request, 'usuarios/perfil.html')
