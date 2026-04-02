from decimal import Decimal
import random
import string
from django.db.models.base import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum

from gestion.models import Cuenta, Transaccion

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)

        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'gestion/login.html')

@login_required
def user_logout(request):

    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('gestion:login')

@login_required
def dashboard(request):
    
    cliente = request.user.cliente    
    
    cuentas = cliente.cuentas.all()   
    cuentas_activas = cuentas.filter(activa=True)
     
    
    saldo_total = cuentas.aggregate(Sum('saldo_disponible'))['saldo_disponible__sum'] or 0    
    
    context = {
        'cuentas': cuentas,
        'cuentas_activas': cuentas_activas,
        'saldo_total': saldo_total,
    }
    
    return render(request, 'gestion/dashboard.html', context)

@login_required
def agregar_cuenta(request):

    if request.method == 'GET':

        context = {
            'tipos_cuenta': Cuenta.TIPO_CUENTA_CHOICES
        }
        
        return render(request, 'gestion/agregar_cuenta.html', context)
    
    if request.method == 'POST':
        
        tipo_cuenta = request.POST.get('tipo')
        saldo_inicial = request.POST.get('saldo', 0)        
        
        num_aleatorio = ''.join(random.choices(string.digits, k=12))
        num_cuenta = f"{tipo_cuenta}-{num_aleatorio}"
        
        Cuenta.objects.create(
            cliente=request.user.cliente,
            tipo=tipo_cuenta,
            numero=num_cuenta,
            saldo_disponible=saldo_inicial
        )
        
        return redirect('gestion:dashboard')
    

@login_required    
def administrar_cuentas(request):
    
    cuentas = request.user.cliente.cuentas.all()
    
    context = {
        'cuentas': cuentas
    }
    
    return render(request, 'gestion/administrar_cuentas.html', context)

@login_required
def eliminar_cuenta(request, cuenta_id):
    
    cuenta = Cuenta.objects.get(id=cuenta_id)

    if request.method == 'GET':

        context = {
            'cuenta': cuenta
        }

        return render(request, 'gestion/eliminar_cuenta.html', context)
    
    
    if request.method == 'POST':
        
        cuenta.delete()        
        return redirect('gestion:administrar_cuentas')

@login_required
def actualizar_cuenta(request, cuenta_id):
    
    cuenta = Cuenta.objects.get(id=cuenta_id)

    if request.method == 'GET':

        context = {
            'cuenta': cuenta
        }

        return render(request, 'gestion/actualizar_cuenta.html', context)
    
    if request.method == 'POST':
        
        nuevo_saldo = request.POST.get('saldo_disponible')
        estado_activo = request.POST.get('activa') == 'on'         
        
        cuenta.saldo_disponible = nuevo_saldo
        cuenta.activa = estado_activo
        cuenta.save()
        
        return redirect('gestion:administrar_cuentas')

@login_required
def transferencias(request):

    cuentas = request.user.cliente.cuentas.all()

    if request.method == 'GET':
        return render(request, 'gestion/transferencias.html', {'cuentas': cuentas})
    
    if request.method == 'POST':
        
        id_origen = request.POST.get('cuenta_origen')
        num_destino = request.POST.get('numero_destino')
        monto = Decimal(request.POST.get('monto'))
        desc = request.POST.get('descripcion')

        
        origen = get_object_or_404(Cuenta, id=id_origen, cliente=request.user.cliente)

        
        try:
            destino = Cuenta.objects.get(numero=num_destino)

        except Cuenta.DoesNotExist:
            destino = None
        
        if origen.saldo_disponible < monto:
            messages.error(request, "Saldo insuficiente en la cuenta de origen.")
        else:
        
            with transaction.atomic():
            
                origen.saldo_disponible -= monto
                origen.save()
            
                if destino:
                    destino.saldo_disponible += monto
                    destino.save()
                
                Transaccion.objects.create(
                    cuenta_origen=origen,
                    cuenta_destino=destino,
                    tipo='transferencia',
                    monto=monto,
                    descripcion=desc
                )
                messages.success(request, "¡Transferencia realizada con éxito!")
                return redirect('gestion:dashboard')


@login_required
def transacciones(request):
    
    transacciones = Transaccion.objects.filter(
        Q(cuenta_origen__cliente=request.user.cliente) | 
        Q(cuenta_destino__cliente=request.user.cliente)
    ).select_related('cuenta_origen', 'cuenta_destino').order_by('-fecha_transaccion')
    
    return render(request, 'gestion/transacciones.html', {'transacciones': transacciones})

def pagina_404_personalizada(request, exception=None):
    return render(request, 'gestion/404.html', status=404)