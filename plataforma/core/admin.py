# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Local, Jornada, Tarea
from .forms import UsuarioCreationForm

class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    model = Usuario
    list_display = ('email', 'first_name', 'last_name', 'rol', 'is_active', 'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'telefono', 'fecha_nacimiento', 'local')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('email', 'first_name', 'last_name', 'telefono', 'rol', 'local'),
        }),
    )


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Mostrar la clave generada en el admin como mensaje
        if not change and hasattr(form, 'get_generated_password'):
            password = form.get_generated_password()
            if password:
                self.message_user(request, f"✅ Usuario creado con contraseña: {password}")

@admin.register(Jornada)
class JornadaAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'fecha', 'hora_inicio', 'hora_fin', 'horas_extras')
    list_filter = ('trabajador', 'fecha')
    search_fields = ('trabajador__email', 'fecha')
    ordering = ('-fecha',)

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Local)
admin.site.register(Tarea)