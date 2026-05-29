from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from master.models import Area, Cargo, Aspirante


class Command(BaseCommand):
    help = 'Llena la base de datos con datos de ejemplo para aspirantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar datos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando datos existentes...')
            Aspirante.objects.all().delete()
            Cargo.objects.all().delete()
            Area.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Datos existentes eliminados.')
            )

        # Crear áreas
        self.create_areas()
        
        # Crear cargos
        self.create_cargos()
        
        # Crear aspirantes
        self.create_aspirantes()
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos de ejemplo creados exitosamente!')
        )

    def create_areas(self):
        """Crear áreas de la empresa"""
        areas_data = [
            {
                'nombre': 'Tecnología',
                'descripcion': 'Desarrollo de software y sistemas informáticos'
            },
            {
                'nombre': 'Recursos Humanos',
                'descripcion': 'Gestión del talento humano y desarrollo organizacional'
            },
            {
                'nombre': 'Marketing',
                'descripcion': 'Estrategias de marketing y comunicación'
            },
            {
                'nombre': 'Ventas',
                'descripcion': 'Gestión comercial y atención al cliente'
            },
            {
                'nombre': 'Finanzas',
                'descripcion': 'Gestión financiera y contable'
            },
            {
                'nombre': 'Operaciones',
                'descripcion': 'Gestión de operaciones y procesos'
            },
            {
                'nombre': 'Diseño',
                'descripcion': 'Diseño gráfico y experiencia de usuario'
            },
            {
                'nombre': 'Calidad',
                'descripcion': 'Aseguramiento de calidad y control de procesos'
            }
        ]

        for area_data in areas_data:
            area, created = Area.objects.get_or_create(
                nombre=area_data['nombre'],
                defaults=area_data
            )
            if created:
                self.stdout.write(f'Área creada: {area.nombre}')

    def create_cargos(self):
        """Crear cargos para cada área"""
        cargos_data = {
            'Tecnología': [
                {'nombre': 'Desarrollador Full Stack', 'nivel': 'Junior', 'salario_minimo': 2500, 'salario_maximo': 3500},
                {'nombre': 'Desarrollador Backend', 'nivel': 'Semi-Senior', 'salario_minimo': 3500, 'salario_maximo': 4500},
                {'nombre': 'Desarrollador Frontend', 'nivel': 'Semi-Senior', 'salario_minimo': 3200, 'salario_maximo': 4200},
                {'nombre': 'Arquitecto de Software', 'nivel': 'Senior', 'salario_minimo': 5000, 'salario_maximo': 7000},
                {'nombre': 'DevOps Engineer', 'nivel': 'Senior', 'salario_minimo': 4500, 'salario_maximo': 6000},
                {'nombre': 'Analista de Sistemas', 'nivel': 'Junior', 'salario_minimo': 2200, 'salario_maximo': 3000},
            ],
            'Recursos Humanos': [
                {'nombre': 'Especialista en RRHH', 'nivel': 'Junior', 'salario_minimo': 2000, 'salario_maximo': 2800},
                {'nombre': 'Coordinador de RRHH', 'nivel': 'Semi-Senior', 'salario_minimo': 2800, 'salario_maximo': 3800},
                {'nombre': 'Gerente de RRHH', 'nivel': 'Senior', 'salario_minimo': 4000, 'salario_maximo': 5500},
                {'nombre': 'Especialista en Reclutamiento', 'nivel': 'Junior', 'salario_minimo': 1800, 'salario_maximo': 2500},
            ],
            'Marketing': [
                {'nombre': 'Especialista en Marketing Digital', 'nivel': 'Junior', 'salario_minimo': 2200, 'salario_maximo': 3000},
                {'nombre': 'Coordinador de Marketing', 'nivel': 'Semi-Senior', 'salario_minimo': 3000, 'salario_maximo': 4000},
                {'nombre': 'Gerente de Marketing', 'nivel': 'Senior', 'salario_minimo': 4500, 'salario_maximo': 6000},
                {'nombre': 'Community Manager', 'nivel': 'Junior', 'salario_minimo': 1800, 'salario_maximo': 2500},
            ],
            'Ventas': [
                {'nombre': 'Ejecutivo de Ventas', 'nivel': 'Junior', 'salario_minimo': 1500, 'salario_maximo': 2500},
                {'nombre': 'Coordinador de Ventas', 'nivel': 'Semi-Senior', 'salario_minimo': 2500, 'salario_maximo': 3500},
                {'nombre': 'Gerente de Ventas', 'nivel': 'Senior', 'salario_minimo': 4000, 'salario_maximo': 6000},
                {'nombre': 'Asesor Comercial', 'nivel': 'Junior', 'salario_minimo': 1200, 'salario_maximo': 2000},
            ],
            'Finanzas': [
                {'nombre': 'Asistente Contable', 'nivel': 'Junior', 'salario_minimo': 1800, 'salario_maximo': 2500},
                {'nombre': 'Contador', 'nivel': 'Semi-Senior', 'salario_minimo': 2500, 'salario_maximo': 3500},
                {'nombre': 'Analista Financiero', 'nivel': 'Semi-Senior', 'salario_minimo': 3000, 'salario_maximo': 4000},
                {'nombre': 'Gerente Financiero', 'nivel': 'Senior', 'salario_minimo': 4500, 'salario_maximo': 6000},
            ],
            'Operaciones': [
                {'nombre': 'Coordinador de Operaciones', 'nivel': 'Junior', 'salario_minimo': 2000, 'salario_maximo': 2800},
                {'nombre': 'Supervisor de Operaciones', 'nivel': 'Semi-Senior', 'salario_minimo': 2800, 'salario_maximo': 3800},
                {'nombre': 'Gerente de Operaciones', 'nivel': 'Senior', 'salario_minimo': 4000, 'salario_maximo': 5500},
            ],
            'Diseño': [
                {'nombre': 'Diseñador Gráfico', 'nivel': 'Junior', 'salario_minimo': 2000, 'salario_maximo': 2800},
                {'nombre': 'Diseñador UX/UI', 'nivel': 'Semi-Senior', 'salario_minimo': 3000, 'salario_maximo': 4000},
                {'nombre': 'Diseñador Senior', 'nivel': 'Senior', 'salario_minimo': 4000, 'salario_maximo': 5500},
            ],
            'Calidad': [
                {'nombre': 'Analista de Calidad', 'nivel': 'Junior', 'salario_minimo': 2200, 'salario_maximo': 3000},
                {'nombre': 'Coordinador de Calidad', 'nivel': 'Semi-Senior', 'salario_minimo': 3000, 'salario_maximo': 4000},
                {'nombre': 'Gerente de Calidad', 'nivel': 'Senior', 'salario_minimo': 4500, 'salario_maximo': 6000},
            ]
        }

        for area_nombre, cargos in cargos_data.items():
            try:
                area = Area.objects.get(nombre=area_nombre)
                for cargo_data in cargos:
                    cargo, created = Cargo.objects.get_or_create(
                        area=area,
                        nombre=cargo_data['nombre'],
                        defaults={
                            'descripcion': f'Cargo de {cargo_data["nivel"]} en {area_nombre}',
                            'nivel': cargo_data['nivel'],
                            'salario_minimo': cargo_data['salario_minimo'],
                            'salario_maximo': cargo_data['salario_maximo']
                        }
                    )
                    if created:
                        self.stdout.write(f'Cargo creado: {cargo.nombre} - {area.nombre}')
            except Area.DoesNotExist:
                self.stdout.write(f'Área no encontrada: {area_nombre}')

    def create_aspirantes(self):
        """Crear aspirantes de ejemplo"""
        nombres = [
            'Juan Carlos', 'María Elena', 'Carlos Alberto', 'Ana Patricia', 'Luis Fernando',
            'Carmen Rosa', 'Pedro Antonio', 'Sofia Alejandra', 'Diego Armando', 'Valeria Cristina',
            'Roberto Carlos', 'Gabriela María', 'Andrés Felipe', 'Natalia Andrea', 'Sebastián David',
            'Isabella Camila', 'Miguel Ángel', 'Daniela Alejandra', 'Alejandro José', 'Laura Valentina',
            'Fernando José', 'Paola Andrea', 'Ricardo Antonio', 'Claudia Patricia', 'Jorge Luis',
            'Monica Liliana', 'Héctor Manuel', 'Sandra Milena', 'Oscar Eduardo', 'Patricia Elena'
        ]
        
        apellidos_paternos = [
            'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez',
            'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández', 'Díaz', 'Moreno',
            'Muñoz', 'Álvarez', 'Romero', 'Alonso', 'Gutiérrez', 'Navarro', 'Torres', 'Domínguez',
            'Vázquez', 'Ramos', 'Gil', 'Ramírez', 'Serrano', 'Blanco', 'Suárez'
        ]
        
        apellidos_maternos = [
            'Silva', 'Castro', 'Ortega', 'Delgado', 'Morales', 'Mendoza', 'Guerrero',
            'Rojas', 'Vera', 'Flores', 'Espinoza', 'Aguilar', 'Vega', 'Campos', 'Reyes',
            'Medina', 'Herrera', 'Vargas', 'Cruz', 'Ramos', 'Peña', 'Sandoval', 'Contreras',
            'Miranda', 'Valencia', 'Fuentes', 'Cortés', 'Paredes', 'León', 'Cabrera'
        ]

        emails_dominios = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'live.com']
        
        estados_postulacion = ['POSTULADO', 'EN_REVISION', 'ENTREVISTA', 'EVALUACION', 'APROBADO', 'RECHAZADO']
        
        niveles_educacion = [
            'Bachiller', 'Técnico', 'Tecnólogo', 'Universitario', 'Postgrado', 'Maestría'
        ]
        
        instituciones_educacion = [
            'Universidad Nacional', 'Universidad de Lima', 'PUCP', 'Universidad San Martín',
            'Universidad Ricardo Palma', 'SENATI', 'TECSUP', 'Instituto San Ignacio',
            'Universidad César Vallejo', 'Universidad Privada del Norte'
        ]

        # Obtener todos los cargos disponibles
        cargos = list(Cargo.objects.all())
        
        if not cargos:
            self.stdout.write(
                self.style.ERROR('No hay cargos disponibles. Creando cargos primero...')
            )
            return

        aspirantes_creados = 0
        
        for i in range(50):  # Crear 50 aspirantes
            # Datos personales
            nombre = random.choice(nombres)
            apellido_paterno = random.choice(apellidos_paternos)
            apellido_materno = random.choice(apellidos_maternos)
            
            # Generar documento único
            numero_documento = f"{random.randint(10000000, 99999999)}"
            while Aspirante.objects.filter(numero_documento=numero_documento).exists():
                numero_documento = f"{random.randint(10000000, 99999999)}"
            
            # Fecha de nacimiento (entre 18 y 65 años)
            fecha_nacimiento = date.today() - timedelta(days=random.randint(18*365, 65*365))
            
            # Fecha de postulación (últimos 6 meses)
            fecha_postulacion = timezone.now() - timedelta(days=random.randint(1, 180))
            
            # Datos de contacto
            celular = f"9{random.randint(10000000, 99999999)}"
            email = f"{nombre.lower().replace(' ', '')}.{apellido_paterno.lower()}{random.randint(1, 99)}@{random.choice(emails_dominios)}"
            
            # Dirección
            distritos = ['Lima', 'Miraflores', 'San Isidro', 'La Molina', 'Surco', 'Pueblo Libre', 'Jesús María', 'Magdalena']
            provincias = ['Lima', 'Callao', 'Arequipa', 'Cusco', 'Trujillo']
            departamentos = ['Lima', 'Callao', 'Arequipa', 'Cusco', 'La Libertad']
            
            # Datos laborales
            cargo_postulado = random.choice(cargos)
            experiencia_anios = random.randint(0, 15)
            estado_postulacion = random.choice(estados_postulacion)
            
            # Crear aspirante
            aspirante = Aspirante.objects.create(
                tipo_documento='DNI',
                numero_documento=numero_documento,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                nombres=nombre,
                fecha_nacimiento=fecha_nacimiento,
                sexo=random.choice(['M', 'F']),
                estado_civil=random.choice(['SOLTERO', 'CASADO', 'DIVORCIADO', 'CONVIVIENTE']),
                celular=celular,
                email=email,
                direccion=f"Av. {random.choice(['Larco', 'Javier Prado', 'Arequipa', 'Tacna'])} {random.randint(100, 9999)}",
                distrito=random.choice(distritos),
                provincia=random.choice(provincias),
                departamento=random.choice(departamentos),
            )
            
            aspirantes_creados += 1
            
            if aspirantes_creados % 10 == 0:
                self.stdout.write(f'Aspirantes creados: {aspirantes_creados}')

        self.stdout.write(
            self.style.SUCCESS(f'Total de aspirantes creados: {aspirantes_creados}')
        )
