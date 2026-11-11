from django.urls import path

from . import views, views_gestion

app_name = 'catering'

urlpatterns = [
    # Público
    path('', views.catalogo, name='catalogo'),
    path('servicio/<slug:slug>/', views.detalle, name='detalle'),

    # Backoffice (solo staff)
    path('gestion/', views_gestion.gestion_lista, name='gestion'),
    path('gestion/nuevo/', views_gestion.servicio_crear, name='servicio_crear'),
    path('gestion/<int:pk>/editar/', views_gestion.servicio_editar, name='servicio_editar'),
    path('gestion/<int:pk>/baja/', views_gestion.servicio_baja, name='servicio_baja'),
    path('gestion/<int:pk>/reactivar/', views_gestion.servicio_reactivar, name='servicio_reactivar'),
]
