
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('mes/<str:anio_mes>/', views.detalle_mes, name='detalle_mes'),
    path('transacciones/', views.lista_transacciones, name='lista_transacciones'),
    path('transacciones/nueva/', views.nueva_transaccion, name='nueva_transaccion'),
    path('transacciones/<int:pk>/eliminar/', views.eliminar_transaccion, name='eliminar_transaccion'),
]
