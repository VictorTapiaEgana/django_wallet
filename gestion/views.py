import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from gestion.models import Cuenta

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

        cuenta_origen_id = request.POST.get('cuenta_origen')
        numero_destino = request.POST.get('numero_destino')
        monto = request.POST.get('monto')
        
        
        
        
        return redirect('gestion:transferencias')




def pagina_404_personalizada(request, exception=None):
    return render(request, 'gestion/404.html', status=404)