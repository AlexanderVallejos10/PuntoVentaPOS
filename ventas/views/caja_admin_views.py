from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from inventario.models import Sede
from usuarios.decorators import administrador_required
from ventas.models import Caja


@administrador_required
def caja_list(request):
    cajas = Caja.objects.select_related(
        'sede'
    ).order_by(
        'sede__nombre',
        'nombre'
    )

    return render(
        request,
        'ventas/caja/caja_list.html',
        {
            'cajas': cajas
        }
    )


@administrador_required
def caja_create(request):
    sedes = Sede.objects.filter(
        activo=True
    )

    if request.method == 'POST':

        Caja.objects.create(
            sede_id=request.POST.get('sede'),
            nombre=request.POST.get('nombre'),
            activa='activa' in request.POST
        )

        messages.success(
            request,
            'Caja creada correctamente.'
        )

        return redirect(
            'ventas:caja_list'
        )

    return render(
        request,
        'ventas/caja/caja_form.html',
        {
            'sedes': sedes,
            'editar': False
        }
    )


@administrador_required
def caja_update(request, caja_id):
    caja = get_object_or_404(
        Caja,
        id=caja_id
    )

    sedes = Sede.objects.filter(
        activo=True
    )

    if request.method == 'POST':
        caja.nombre = request.POST.get(
            'nombre'
        )

        caja.sede_id = request.POST.get(
            'sede'
        )

        caja.activa = (
            'activa'
            in request.POST
        )

        caja.save()

        messages.success(
            request,
            'Caja actualizada.'
        )

        return redirect(
            'ventas:caja_list'
        )

    return render(
        request,
        'ventas/caja/caja_form.html',
        {
            'caja': caja,
            'sedes': sedes,
            'editar': True
        }
    )


@administrador_required
def caja_delete(request, caja_id):
    caja = get_object_or_404(
        Caja,
        id=caja_id
    )

    caja.delete()

    messages.success(
        request,
        'Caja eliminada.'
    )

    return redirect(
        'ventas:caja_list'
    )