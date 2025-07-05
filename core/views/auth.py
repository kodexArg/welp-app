"""
Vistas de autenticación y gestión de sesiones.

Este módulo contiene todas las vistas relacionadas con el login,
logout y gestión de sesiones de usuario.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    """Vista de inicio de sesión con autenticación"""
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'core:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    """Vista de cierre de sesión"""
    if request.method == 'POST':
        # Limpiar todos los mensajes existentes antes de logout
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # Esto consume y limpia todos los mensajes
        storage.used = True
        
        logout(request)
        # Redirigir directamente al login sin mensaje para evitar duplicados
        return redirect('core:login')
    return redirect('core:index') 