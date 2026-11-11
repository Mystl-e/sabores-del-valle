from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'perfil'
    fk_name = 'usuario'


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff', 'is_active')
    list_filter = BaseUserAdmin.list_filter + ('perfil__rol',)
    list_select_related = ('perfil',)

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    @admin.display(description='Rol', ordering='perfil__rol')
    def rol(self, obj):
        perfil = getattr(obj, 'perfil', None)
        return perfil.get_rol_display() if perfil else '—'