from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout
from django.http import JsonResponse

from rest_framework import viewsets
from .models import Local, Usuario, Tarea, Jornada
from .serializers import LocalSerializer, UsuarioSerializer, TareaSerializer, JornadaSerializer

from .forms import PerfilUpdateForm




# Vista para manejar las operaciones CRUD de los modelos
class LocalViewSet(viewsets.ModelViewSet):
    queryset = Local.objects.all()
    serializer_class = LocalSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer

class JornadaViewSet(viewsets.ModelViewSet):
    queryset = Jornada.objects.all()
    serializer_class = JornadaSerializer

# Vista para manejar el inicio de sesión
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Configurar la sesión para que expire en 24 horas
            request.session.set_expiry(timedelta(hours=24).total_seconds())
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'core/login.html')

@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioCreationForm
from django.core.mail import send_mail
from django.conf import settings

def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user, password = form.save()
            
            # Enviar credenciales por email (opcional)
            if user.email:
                send_mail(
                    'Tus credenciales de acceso',
                    f'''Usuario: {user.username}
Contraseña: {password}

Por favor cambia tu contraseña después del primer acceso.''',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            
            messages.success(request, f'Usuario {user.email} creado exitosamente!')
            return redirect('lista_usuarios')
    else:
        form = UsuarioCreationForm()
    
    return render(request, 'core/crear_usuario.html', {'form': form})


# Vustas del dashboard

@login_required
def dashboard_view(request):
    mensajes_no_leidos = 3  # esto luego lo traés de tu modelo real
    return render(request, 'core/dashboard.html', {'mensajes_no_leidos': mensajes_no_leidos})

@login_required
def noticias_view(request):
    return render(request, 'core/news.html')

@login_required
def horario_view(request):
    return render(request, 'core/horario.html')

@login_required
def nominas_view(request):
    return render(request, 'core/nominas.html')

@login_required
def perfil_view(request):
    if request.method == 'POST':
        form = PerfilUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado correctamente!')
            return redirect('perfil')
    else:
        form = PerfilUpdateForm(instance=request.user)

    return render(request, 'core/perfil.html', {'form': form})



@login_required
def api_horarios(request):
    user = request.user
    jornadas = Jornada.objects.filter(trabajador=user).order_by('-fecha')
    
    data = []
    for jornada in jornadas:
        data.append({
            'fecha': jornada.fecha.strftime('%Y-%m-%d'),
            'hora_inicio': jornada.hora_inicio.strftime('%H:%M'),
            'hora_fin': jornada.hora_fin.strftime('%H:%M'),
            'horas_extras': str(jornada.horas_extras),
            'observaciones': jornada.observaciones or '',
        })
    
    return JsonResponse(data, safe=False)


@login_required
def horario_view(request):
    user = request.user
    jornadas = Jornada.objects.filter(trabajador=user).order_by('-fecha')
    return render(request, 'core/horario.html', {'jornadas': jornadas})
