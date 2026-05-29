from django.db import migrations


def normalizar_ruta_archivo(nombre):
    if not nombre:
        return nombre
    nombre = str(nombre).replace('\\', '/')
    while nombre.startswith('media/'):
        nombre = nombre[6:]
    return nombre


def corregir_rutas_cv(apps, schema_editor):
    CV = apps.get_model('master', 'CV')
    for cv in CV.objects.exclude(cv_archivo='').exclude(cv_archivo__isnull=True):
        ruta_actual = cv.cv_archivo
        ruta_normalizada = normalizar_ruta_archivo(ruta_actual)
        if ruta_normalizada != ruta_actual:
            cv.cv_archivo = ruta_normalizada
            cv.save(update_fields=['cv_archivo'])


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0005_persona_user'),
    ]

    operations = [
        migrations.RunPython(corregir_rutas_cv, migrations.RunPython.noop),
    ]
