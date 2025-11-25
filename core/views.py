from datetime import datetime
from django.shortcuts import redirect
from .forms import TransaccionForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404

from .models import ResumenMensual, GastoPorCategoriaMes, Transaccion


@login_required
def lista_transacciones(request):
    transacciones = (
        Transaccion.objects
        .filter(cuenta__owner=request.user)
        .select_related('cuenta', 'categoria')
        .order_by('-fecha')
    )

    total = transacciones.aggregate(total=Sum('monto'))['total'] or 0

    return render(request, 'core/transacciones_lista.html', {
        'transacciones': transacciones,
        'total': total,
    })


@login_required
def nueva_transaccion(request):
    if request.method == 'POST':
        form = TransaccionForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('core:lista_transacciones')
    else:
        form = TransaccionForm(user=request.user)

    return render(request, 'core/transaccion_form.html', {'form': form})
@login_required
def inicio(request):
    """
    Página de inicio: muestra todos los meses con su resumen.
    Solo usuarios logueados pueden ver esto.
    """
    resumenes = ResumenMensual.objects.order_by('-anio_mes')
    context = {
        'resumenes': resumenes,
    }
    return render(request, 'core/inicio.html', context)

@login_required
def eliminar_transaccion(request, pk):
    """
    Permite borrar una transacción si pertenece a una cuenta del usuario logueado.
    pk = id de la transacción.
    """
    transaccion = get_object_or_404(
        Transaccion,
        pk=pk,
        cuenta__owner=request.user,  
    )

    if request.method == 'POST':
        transaccion.delete()
        return redirect('core:lista_transacciones')

    return render(request, 'core/transaccion_confirm_delete.html', {
        'transaccion': transaccion,
    })


@login_required
def detalle_mes(request, anio_mes):
    """
    Detalle de un mes: lista transacciones y gasto por categoría.
    anio_mes viene en formato 'YYYY-MM'
    """

    try:
        datetime.strptime(anio_mes, "%Y-%m")
    except ValueError:
        return render(request, 'core/error.html', {'mensaje': 'Formato de mes inválido'})

    resumen = get_object_or_404(ResumenMensual, anio_mes=anio_mes)


    gastos_categoria = GastoPorCategoriaMes.objects.filter(anio_mes=anio_mes)

    anio = int(anio_mes.split('-')[0])
    mes = int(anio_mes.split('-')[1])

    transacciones = (
        Transaccion.objects
        .filter(fecha__year=anio, fecha__month=mes, cuenta__owner=request.user,  )
        .select_related('cuenta', 'categoria')
        .order_by('-fecha')
    )


    total_ingresos = transacciones.filter(categoria__tipo='ingreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    total_gastos = transacciones.filter(categoria__tipo='gasto').aggregate(
        total=Sum('monto')
    )['total'] or 0

    total_gastos = -total_gastos

    context = {
        'anio_mes': anio_mes,
        'resumen': resumen,
        'gastos_categoria': gastos_categoria,
        'transacciones': transacciones,
        'total_ingresos_calc': total_ingresos,
        'total_gastos_calc': total_gastos,
    }
    return render(request, 'core/detalle_mes.html', context)
