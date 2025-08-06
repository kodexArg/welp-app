"""
Vistas de autenticación y gestión de sesiones.

Este módulo contiene todas las vistas relacionadas con el login,
logout y gestión de sesiones de usuario.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

def login_view(request):
    """Vista de inicio de sesión con autenticación y control de intentos fallidos"""
    if request.user.is_authenticated:
        return redirect('core:index')
    
    # Obtener IP del cliente
    client_ip = get_client_ip(request)
    
    # Verificar si la IP está bloqueada
    if is_ip_blocked(request, client_ip):
        remaining_time = get_remaining_block_time(request, client_ip)
        messages.error(request, f'Demasiados intentos fallidos. Intenta nuevamente en {remaining_time} minutos.')
        return render(request, 'core/login.html', {'password_error': True})
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Login exitoso - limpiar intentos fallidos
                clear_failed_attempts(request, client_ip)
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'core:index')
                return redirect(next_url)
            else:
                # Login fallido - incrementar contador
                failed_attempts = increment_failed_attempts(request, client_ip)
                
                if failed_attempts >= 5:
                    # Bloquear IP por 5 minutos
                    block_ip(request, client_ip)
                    messages.error(request, 'Demasiados intentos fallidos. Tu IP ha sido bloqueada por 5 minutos.')
                else:
                    remaining_attempts = 5 - failed_attempts
                    messages.error(request, f'Usuario o contraseña incorrectos. Te quedan {remaining_attempts} intentos.')
                
                return render(request, 'core/login.html', {'password_error': True})
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    """Vista de cierre de sesión"""
    if request.method == 'POST':
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        storage.used = True
        
        logout(request)
        return redirect('core:login')
    return redirect('core:index')


def get_client_ip(request):
    """Obtener la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_session_key(client_ip, key_type):
    """Generar clave de sesión para el control de intentos"""
    return f'login_{key_type}_{client_ip}'


def increment_failed_attempts(request, client_ip):
    """Incrementar contador de intentos fallidos para una IP"""
    key = get_session_key(client_ip, 'attempts')
    attempts = request.session.get(key, 0) + 1
    request.session[key] = attempts
    return attempts


def clear_failed_attempts(request, client_ip):
    """Limpiar intentos fallidos para una IP"""
    attempts_key = get_session_key(client_ip, 'attempts')
    block_key = get_session_key(client_ip, 'blocked_until')
    
    if attempts_key in request.session:
        del request.session[attempts_key]
    if block_key in request.session:
        del request.session[block_key]


def block_ip(request, client_ip):
    """Bloquear IP por 5 minutos"""
    block_until = timezone.now() + timedelta(minutes=5)
    block_key = get_session_key(client_ip, 'blocked_until')
    request.session[block_key] = block_until.isoformat()


def is_ip_blocked(request, client_ip):
    """Verificar si una IP está bloqueada"""
    block_key = get_session_key(client_ip, 'blocked_until')
    block_until_str = request.session.get(block_key)
    
    if not block_until_str:
        return False
    
    try:
        block_until = timezone.datetime.fromisoformat(block_until_str)
        if timezone.is_naive(block_until):
            block_until = timezone.make_aware(block_until)
        return timezone.now() < block_until
    except (ValueError, TypeError):
        # Si hay error parseando la fecha, limpiar la sesión
        del request.session[block_key]
        return False


def get_remaining_block_time(request, client_ip):
    """Obtener tiempo restante de bloqueo en minutos"""
    block_key = get_session_key(client_ip, 'blocked_until')
    block_until_str = request.session.get(block_key)
    
    if not block_until_str:
        return 0
    
    try:
        block_until = timezone.datetime.fromisoformat(block_until_str)
        if timezone.is_naive(block_until):
            block_until = timezone.make_aware(block_until)
        
        remaining = block_until - timezone.now()
        return max(0, int(remaining.total_seconds() / 60))
    except (ValueError, TypeError):
        return 0