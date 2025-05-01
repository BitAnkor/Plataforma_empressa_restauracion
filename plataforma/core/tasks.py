from datetime import timedelta, time
from django.utils import timezone
from .models import Usuario, Jornada

def generar_jornadas_proxima_semana():
    hoy = timezone.now().date()
    lunes = hoy + timedelta(days=(7 - hoy.weekday()))  # próximo lunes

    for user in Usuario.objects.filter(is_active=True):
        for i in range(5):  # lunes a viernes
            fecha = lunes + timedelta(days=i)
            if not Jornada.objects.filter(trabajador=user, fecha=fecha).exists():
                Jornada.objects.create(
                    trabajador=user,
                    fecha=fecha,
                    hora_inicio=time(9, 0),
                    hora_fin=time(17, 0),
                    horas_extras=0
                )
