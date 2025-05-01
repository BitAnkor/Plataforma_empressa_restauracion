from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Usuario, Jornada
from django.utils import timezone
from datetime import timedelta, time
import random
import string

def generar_contraseña(longitud=12):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def generar_nombre_usuario(nombre, apellido):
    base = f"{nombre.lower()[0]}{apellido.lower().replace(' ', '')}"
    if not Usuario.objects.filter(username=base).exists():
        return base
    i = 1
    while True:
        nuevo_usuario = f"{base}{i}"
        if not Usuario.objects.filter(username=nuevo_usuario).exists():
            return nuevo_usuario
        i += 1

@receiver(post_save, sender=Usuario)
def asignar_credenciales_automaticas(sender, instance, created, **kwargs):
    if created and not instance.username:
        # Generar credenciales solo si es un nuevo usuario sin username
        nombre = instance.first_name or "user"
        apellido = instance.last_name or str(instance.id)
        
        instance.username = generar_nombre_usuario(nombre, apellido)
        password = generar_contraseña()
        instance.set_password(password)
        
        # Guardar solo estos campos para evitar recursión
        Usuario.objects.filter(pk=instance.pk).update(
            username=instance.username,
            password=instance.password
        )
        
        # Opcional: Enviar las credenciales por email
        print(f"Usuario creado: {instance.username} - Contraseña: {password}")

@receiver(post_save, sender=Usuario)
def crear_jornadas_semanales(sender, instance, created, **kwargs):
    if created:
        hoy = timezone.now().date()
        lunes = hoy - timedelta(days=hoy.weekday())  # encontrar el lunes actual

        for i in range(5):  # lunes a viernes
            fecha = lunes + timedelta(days=i)
            Jornada.objects.create(
                trabajador=instance,
                fecha=fecha,
                hora_inicio=time(9, 0),
                hora_fin=time(17, 0),
                horas_extras=0
            )