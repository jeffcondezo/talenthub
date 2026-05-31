import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talenthub.settings')
django.setup()
from django.db import connection
with connection.cursor() as c:
    c.execute(
        'SELECT centro_estudio, HEX(centro_estudio), pais, HEX(pais) '
        'FROM master_formacionacademica WHERE id=2'
    )
    print(c.fetchone())
