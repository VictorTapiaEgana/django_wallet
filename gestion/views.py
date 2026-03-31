from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    return redirect('login')

@login_required

def dashboard(request):
    return render(request, 'gestion/dashboard.html')
