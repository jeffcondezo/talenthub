"""
Sincroniza archivos CV desde static/media/cvs hacia media/cvs
y corrige las rutas guardadas en la base de datos.
"""
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from master.models import CV


def nombre_sin_sufijo_django(nombre_archivo):
    """Quita el sufijo aleatorio que Django añade al guardar (ej. _xq4x8z)."""
    return re.sub(r'_[a-z0-9]{5,8}(\.[^.]+)$', r'\1', nombre_archivo, flags=re.IGNORECASE)


def resolver_archivo_en_static(nombre_bd, archivos_static):
    """Encuentra el archivo real en static/media/cvs para un nombre de BD."""
    solo_nombre = Path(nombre_bd).name

    candidatos = [
        solo_nombre,
        nombre_sin_sufijo_django(solo_nombre),
        re.sub(r'_\d+(\.[^.]+)$', r'\1', nombre_sin_sufijo_django(solo_nombre), flags=re.IGNORECASE),
    ]

    for candidato in candidatos:
        if candidato in archivos_static:
            return candidato

    base = nombre_sin_sufijo_django(solo_nombre)
    base_sin_ext = Path(base).stem
    coincidencias = [f for f in archivos_static if f.startswith(base_sin_ext[:20])]
    if len(coincidencias) == 1:
        return coincidencias[0]

    return None


class Command(BaseCommand):
    help = 'Sincroniza CVs desde static/media/cvs a media/cvs y corrige rutas en BD'

    def handle(self, *args, **options):
        origen = Path(settings.BASE_DIR) / 'static' / 'media' / 'cvs'
        destino = Path(settings.MEDIA_ROOT) / 'cvs'
        destino.mkdir(parents=True, exist_ok=True)

        if not origen.exists():
            self.stderr.write(self.style.ERROR(f'No existe la carpeta origen: {origen}'))
            return

        archivos_static = {
            f.name for f in origen.iterdir() if f.is_file()
        }
        self.stdout.write(f'Archivos en {origen}: {len(archivos_static)}')

        actualizados = 0
        omitidos = 0
        errores = 0

        for cv in CV.objects.exclude(cv_archivo='').exclude(cv_archivo__isnull=True):
            ruta_bd = CV.normalizar_ruta_archivo(cv.cv_archivo.name)
            archivo_real = resolver_archivo_en_static(ruta_bd, archivos_static)

            if not archivo_real:
                self.stderr.write(
                    self.style.WARNING(
                        f'  Sin coincidencia para CV #{cv.id} ({cv.persona}): {ruta_bd}'
                    )
                )
                errores += 1
                continue

            origen_archivo = origen / archivo_real
            destino_archivo = destino / archivo_real
            nueva_ruta = f'cvs/{archivo_real}'

            if not destino_archivo.exists() or origen_archivo.stat().st_mtime > destino_archivo.stat().st_mtime:
                shutil.copy2(origen_archivo, destino_archivo)

            if cv.cv_archivo.name != nueva_ruta:
                cv.cv_archivo.name = nueva_ruta
                cv.save(update_fields=['cv_archivo'])
                self.stdout.write(
                    self.style.SUCCESS(f'  CV #{cv.id}: {ruta_bd} -> {nueva_ruta}')
                )
                actualizados += 1
            else:
                omitidos += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Actualizados: {actualizados}'))
        self.stdout.write(f'Sin cambios: {omitidos}')
        if errores:
            self.stdout.write(self.style.WARNING(f'Sin archivo: {errores}'))
