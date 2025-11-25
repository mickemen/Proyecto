from django.contrib import admin
from .models import (
    Cuenta,
    Categoria,
    Transaccion,
    PresupuestoMensual,
    ResumenMensual,
    GastoPorCategoriaMes,
)


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'moneda')
    search_fields = ('nombre',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nombre',)


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'cuenta', 'categoria', 'descripcion', 'monto')
    list_filter = ('cuenta', 'categoria', 'fecha')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha'


@admin.register(PresupuestoMensual)
class PresupuestoMensualAdmin(admin.ModelAdmin):
    list_display = ('anio', 'mes', 'categoria', 'monto')
    list_filter = ('anio', 'mes', 'categoria')


@admin.register(ResumenMensual)
class ResumenMensualAdmin(admin.ModelAdmin):
    list_display = ('anio_mes', 'ingresos', 'gastos', 'balance')
    list_filter = ('anio_mes',)


@admin.register(GastoPorCategoriaMes)
class GastoPorCategoriaMesAdmin(admin.ModelAdmin):
    list_display = ('anio_mes', 'categoria', 'gasto_total')
    list_filter = ('anio_mes', 'categoria')
