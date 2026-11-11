from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.IngresoView.as_view(), name='login'),
    path('logout/', views.salir, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
]
