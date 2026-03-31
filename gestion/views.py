from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

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
