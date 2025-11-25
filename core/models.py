from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Cuenta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    moneda = models.CharField(max_length=3, default='CRC')
    owner = models.ForeignKey(           
        User,
        on_delete=models.CASCADE,
        db_column='owner_id',            
        null=True,
        blank=True,
    )
    
    class Meta:
        db_table = 'cuentas'
        managed = False   

    def __str__(self):
        return f"{self.nombre} ({self.moneda})"

class Categoria(models.Model):
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    class Meta:
        db_table = 'categorias'
        managed = False  
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return f"{self.nombre} [{self.tipo}]"


class Transaccion(models.Model):
    id = models.BigAutoField(primary_key=True)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, db_column='cuenta_id')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='categoria_id')
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'transacciones'
        managed = False   
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        indexes = [
            models.Index(fields=['fecha'], name='idx_fecha'),
            models.Index(fields=['categoria'], name='idx_categoria'),
        ]

    def __str__(self):
        return f"{self.fecha} - {self.descripcion} ({self.monto})"


class PresupuestoMensual(models.Model):
    id = models.AutoField(primary_key=True)
    anio = models.SmallIntegerField()
    mes = models.SmallIntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='categoria_id')
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'presupuestos_mensuales'
        verbose_name = 'Presupuesto Mensual'
        verbose_name_plural = 'Presupuestos Mensuales'
        managed = False  
        unique_together = ('anio', 'mes', 'categoria')



class ResumenMensual(models.Model):
    
    anio_mes = models.CharField(max_length=7, primary_key=True)
    ingresos = models.DecimalField(max_digits=12, decimal_places=2)
    gastos = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'v_resumen_mensual'
        verbose_name = 'Resumen Mensual'
        verbose_name_plural = 'Resumenes Mensuales'
        managed = False  

    def __str__(self):
        return f"{self.anio_mes} - Balance: {self.balance}"


class GastoPorCategoriaMes(models.Model):
    
    anio_mes = models.CharField(max_length=7, primary_key=True)
    categoria = models.CharField(max_length=80)
    gasto_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'v_gasto_por_categoria_mes'
        verbose_name = 'Gasto por Categoria de Mes'
        verbose_name_plural = 'Gastos por Categorias de Mes'
        managed = False

    def __str__(self):
        return f"{self.anio_mes} - {self.categoria}"