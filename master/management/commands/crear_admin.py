from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from master.models import PerfilAcceso


class Command(BaseCommand):
    help = 'Marca un usuario existente como administrador del sistema.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario Django')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f'Usuario "{username}" no existe.') from exc

        perfil, _ = PerfilAcceso.objects.get_or_create(
            user=user,
            defaults={'es_administrador': True, 'modulos': []},
        )
        perfil.es_administrador = True
        perfil.modulos = []
        perfil.save()
        self.stdout.write(self.style.SUCCESS(f'"{username}" es ahora administrador.'))
