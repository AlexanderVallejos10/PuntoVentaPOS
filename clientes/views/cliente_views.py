from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from clientes.forms import ClienteForm
from clientes.models import Cliente
from clientes.services.documento_service import DocumentoService
from usuarios.decorators import vendedor_required
from ventas.services.reglas_peru import documento_valido, limpiar_documento


@vendedor_required
def buscar_documento(request):
    tipo_documento = request.GET.get('tipo_documento', '').upper().strip()
    numero_documento = limpiar_documento(request.GET.get('numero_documento'))

    if tipo_documento not in ['DNI', 'RUC']:
        return JsonResponse({
            'ok': False,
            'mensaje': 'La consulta automática solo está disponible para DNI o RUC.'
        })

    if not documento_valido(tipo_documento, numero_documento):
        return JsonResponse({
            'ok': False,
            'mensaje': 'Revise el número de documento.'
        })

    if tipo_documento == 'DNI':
        return JsonResponse(DocumentoService.buscar_dni(numero_documento))

    return JsonResponse(DocumentoService.buscar_ruc(numero_documento))


@vendedor_required
def cliente_list(request):
    buscar = request.GET.get('buscar', '').strip()

    clientes = Cliente.objects.all().order_by('nombre')

    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar)
            | Q(numero_documento__icontains=buscar)
            | Q(tipo_documento__icontains=buscar)
            | Q(telefono__icontains=buscar)
            | Q(email__icontains=buscar)
        )

    return render(
        request,
        'clientes/cliente_list.html',
        {
            'clientes': clientes,
            'buscar': buscar,
        }
    )


@vendedor_required
def cliente_create(request):
    form = ClienteForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('clientes:cliente_list')

    return render(
        request,
        'clientes/cliente_form.html',
        {
            'form': form,
            'titulo': 'Registrar cliente',
        }
    )


@vendedor_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('clientes:cliente_list')

    return render(
        request,
        'clientes/cliente_form.html',
        {
            'form': form,
            'titulo': 'Editar cliente',
        }
    )


@vendedor_required
def cliente_create_ajax(request):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'error': 'Método no permitido.'
        })

    tipo_documento = request.POST.get('tipo_documento', 'SD').upper().strip() or 'SD'
    numero_documento = limpiar_documento(request.POST.get('numero_documento'))
    nombre = request.POST.get('nombre', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    email = request.POST.get('email', '').strip()
    direccion = request.POST.get('direccion', '').strip()

    if tipo_documento not in ['SD', 'DNI', 'RUC', 'CE']:
        return JsonResponse({
            'ok': False,
            'error': 'Tipo de documento no válido.'
        })

    if not nombre:
        return JsonResponse({
            'ok': False,
            'error': 'Ingrese el nombre del cliente.'
        })

    if tipo_documento == 'SD':
        numero_documento = ''
    elif not documento_valido(tipo_documento, numero_documento):
        return JsonResponse({
            'ok': False,
            'error': 'Revise el número de documento.'
        })

    if numero_documento:
        cliente = Cliente.objects.filter(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
        ).first()

        if cliente:
            return JsonResponse({
                'ok': True,
                'id': cliente.id,
                'nombre': cliente.nombre,
                'tipo_documento': cliente.tipo_documento,
                'numero_documento': cliente.numero_documento or '',
                'mensaje': 'El cliente ya existía y fue seleccionado.'
            })

    cliente = Cliente.objects.create(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre=nombre,
        telefono=telefono,
        email=email,
        direccion=direccion,
        activo=True,
    )

    return JsonResponse({
        'ok': True,
        'id': cliente.id,
        'nombre': cliente.nombre,
        'tipo_documento': cliente.tipo_documento,
        'numero_documento': cliente.numero_documento or '',
        'mensaje': 'Cliente creado correctamente.'
    })
