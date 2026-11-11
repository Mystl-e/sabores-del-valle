from django.urls import path

from . import views

app_name = 'catering'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('servicio/<slug:slug>/', views.detalle, name='detalle'),
]
