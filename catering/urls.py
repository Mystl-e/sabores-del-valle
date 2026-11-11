from django.urls import path

from . import views, views_cotizacion, views_gestion

app_name = 'catering'

urlpatterns = [
    # Público
    path('', views.catalogo, name='catalogo'),
    path('servicio/<slug:slug>/', views.detalle, name='detalle'),

    # Cotizador en sesión
    path('cotizacion/', views_cotizacion.ver_cotizacion, name='cotizacion'),
    path('cotizacion/agregar/<int:pk>/', views_cotizacion.agregar, name='cotizacion_agregar'),
    path('cotizacion/actualizar/<int:pk>/', views_cotizacion.actualizar, name='cotizacion_actualizar'),
    path('cotizacion/eliminar/<int:pk>/', views_cotizacion.eliminar, name='cotizacion_eliminar'),
    path('cotizacion/vaciar/', views_cotizacion.vaciar, name='cotizacion_vaciar'),
    path('cotizacion/confirmar/', views_cotizacion.confirmar, name='cotizacion_confirmar'),
    path('cotizacion/comprobante/', views_cotizacion.comprobante, name='comprobante'),

    # Backoffice (solo staff)
    path('gestion/', views_gestion.gestion_lista, name='gestion'),
    path('gestion/nuevo/', views_gestion.servicio_crear, name='servicio_crear'),
    path('gestion/<int:pk>/editar/', views_gestion.servicio_editar, name='servicio_editar'),
    path('gestion/<int:pk>/baja/', views_gestion.servicio_baja, name='servicio_baja'),
    path('gestion/<int:pk>/reactivar/', views_gestion.servicio_reactivar, name='servicio_reactivar'),
]
