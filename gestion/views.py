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
    
    saldo_total = cuentas.aggregate(Sum('saldo_disponible'))['saldo_disponible__sum'] or 0    
    
    context = {
        'cuentas': cuentas,
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
        
        prefijo = "BCI" if tipo_cuenta == "BCI" else "BTC"
        num_aleatorio = ''.join(random.choices(string.digits, k=12))
        num_cuenta = f"{prefijo}-{num_aleatorio}"
        
        Cuenta.objects.create(
            cliente=request.user.cliente,
            tipo=tipo_cuenta,
            numero=num_cuenta,
            saldo_disponible=saldo_inicial
        )
        return redirect('gestion:dashboard')
    
    
