from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def crear_perfiles_admin_existentes(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    PerfilAcceso = apps.get_model('master', 'PerfilAcceso')
    for user in User.objects.all():
        PerfilAcceso.objects.get_or_create(
            user_id=user.id,
            defaults={
                'es_administrador': True,
                'modulos': [],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master', '0006_fix_cv_archivo_paths'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerfilAcceso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('es_administrador', models.BooleanField(default=False, verbose_name='Administrador')),
                ('modulos', models.JSONField(blank=True, default=list, help_text='Lista de claves de módulo (ej. inicio, colaboradores).', verbose_name='Módulos permitidos')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil_acceso', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Perfil de acceso',
                'verbose_name_plural': 'Perfiles de acceso',
            },
        ),
        migrations.RunPython(crear_perfiles_admin_existentes, migrations.RunPython.noop),
    ]
