from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import secrets
import string

class UsuarioManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        """
        Crea y guarda un usuario con los datos proporcionados.
        Genera automáticamente username y password si no se especifican.
        """
        if not email and not username:
            raise ValueError('Debe proporcionarse al menos email o username')
        
        email = self.normalize_email(email) if email else None
        
        # Generar username automático si no se proporciona
        if not username:
            first_name = extra_fields.get('first_name', 'user')
            last_name = extra_fields.get('last_name', str(secrets.randbelow(1000)))
            base_username = f"{first_name[0].lower()}{last_name.lower().replace(' ', '')}"
            username = base_username
            i = 1
            while Usuario.objects.filter(username=username).exists():
                username = f"{base_username}{i}"
                i += 1
        
        user = self.model(username=username, email=email, **extra_fields)
        
        # Generar contraseña automática si no se proporciona
        if not password:
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        user.set_password(password)
        user.save(using=self._db)
        return user, password

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con los datos proporcionados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'admin_sistema')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class Local(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Locales"
        ordering = ['nombre']

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('trabajador', 'Trabajador'),
        ('admin_local', 'Administrador del Local'),
        ('admin_sistema', 'Administrador del Sistema'),
    ]
    
    # Campos básicos
    email = models.EmailField(_('email address'), unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    necesita_cambio_password = models.BooleanField(default=True)
    
    # Relaciones
    local = models.ForeignKey(Local, on_delete=models.SET_NULL, null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='trabajador')
    
    objects = UsuarioManager()

    # Configuración para autenticación por email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    def save(self, *args, **kwargs):
        # Asegurar que el username esté establecido
        if not self.username:
            base_username = f"{self.first_name[0].lower()}{self.last_name.lower().replace(' ', '')}"
            username = base_username
            i = 1
            while Usuario.objects.filter(username=username).exists():
                username = f"{base_username}{i}"
                i += 1
            self.username = username
        
        super().save(*args, **kwargs)

    @property
    def es_administrador(self):
        return self.rol in ['admin_local', 'admin_sistema'] or self.is_superuser

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']

class Tarea(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
    ]
    
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tareas')
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"

    class Meta:
        verbose_name_plural = "Tareas"
        ordering = ['-fecha', 'estado']

class Jornada(models.Model):
    trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jornadas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    horas_extras = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.trabajador.username} - {self.fecha} ({self.hora_inicio} a {self.hora_fin})"

    class Meta:
        verbose_name_plural = "Jornadas"
        ordering = ['-fecha', 'trabajador']
        unique_together = ['trabajador', 'fecha']


