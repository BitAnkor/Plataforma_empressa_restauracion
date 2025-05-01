from django.urls import path
from .views import login_view, dashboard_view, noticias_view, horario_view, nominas_view, perfil_view, api_horarios
from django.contrib.auth.views import LogoutView, PasswordChangeView

from rest_framework.routers import DefaultRouter
from .views import LocalViewSet, UsuarioViewSet, TareaViewSet, JornadaViewSet

router = DefaultRouter()
router.register(r'locales', LocalViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'tareas', TareaViewSet)
router.register(r'jornadas', JornadaViewSet)




urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('news/', noticias_view, name='news'),
    path('horario/',horario_view, name='horario'),
    path('nominas/', nominas_view, name='nominas'),
    path('perfil/', perfil_view, name='perfil'),
    path('horarios/', api_horarios, name='api_horarios'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('cambiar-contraseña/', PasswordChangeView.as_view(template_name='core/cambiar_contrasena.html', success_url='/perfil/'), name='cambiar_contraseña'),

    
]+ router.urls

