from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Persona(models.Model):
    """
    Modelo base abstracto para el registro de personas
    Contiene todos los datos básicos comunes entre aspirantes y colaboradores
    """
    
    # Opciones para campos de selección
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'DNI'),
        ('CE', 'Carnet de Extranjería'),
        ('PASAPORTE', 'Pasaporte'),
        ('RUC', 'RUC'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('SOLTERO', 'Soltero(a)'),
        ('CASADO', 'Casado(a)'),
        ('DIVORCIADO', 'Divorciado(a)'),
        ('VIUDO', 'Viudo(a)'),
        ('CONVIVIENTE', 'Conviviente'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    # Campos principales
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='DNI',
        verbose_name='Tipo de Documento'
    )
    
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{8,11}$',
                message='El número de documento debe contener entre 8 y 11 dígitos'
            )
        ],
        verbose_name='Número de Documento'
    )
    
    # Nombres
    apellido_paterno = models.CharField(
        max_length=100,
        verbose_name='Apellido Paterno'
    )
    
    apellido_materno = models.CharField(
        max_length=100,
        verbose_name='Apellido Materno'
    )
    
    nombres = models.CharField(
        max_length=150,
        verbose_name='Nombres'
    )
    
    # Datos personales
    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de Nacimiento'
    )
    
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name='Sexo'
    )
    
    estado_civil = models.CharField(
        max_length=20,
        choices=ESTADO_CIVIL_CHOICES,
        verbose_name='Estado Civil'
    )
    
    # Información de contacto
    celular = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9+\-\s()]{7,15}$',
                message='Formato de celular inválido'
            )
        ],
        verbose_name='Celular'
    )
    
    email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        verbose_name='Correo Electrónico'
    )
    
    # Dirección
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    
    distrito = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Distrito'
    )
    
    provincia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Provincia'
    )
    
    departamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento'
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        abstract = True  # Modelo abstracto - no se crea tabla en BD
    
    def __str__(self):
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombres}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo de la persona"""
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"
    
    @property
    def edad(self):
        """Calcula la edad basada en la fecha de nacimiento"""
        if self.fecha_nacimiento:
            today = timezone.now().date()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        from django.core.exceptions import ValidationError
        
        # Validar que la fecha de nacimiento no sea futura
        if self.fecha_nacimiento and self.fecha_nacimiento > timezone.now().date():
            raise ValidationError({
                'fecha_nacimiento': 'La fecha de nacimiento no puede ser futura.'
            })
    
    def save(self, *args, **kwargs):
        """Sobrescribir el método save para aplicar validaciones"""
        self.clean()
        super().save(*args, **kwargs)


class Area(models.Model):
    """
    Modelo para las áreas o departamentos de la empresa
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Área'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Cargo(models.Model):
    """
    Modelo para los cargos o puestos de trabajo
    """
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name='cargos',
        verbose_name='Área'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Cargo'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    nivel = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Nivel'
    )
    
    salario_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Salario Mínimo'
    )
    
    salario_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Salario Máximo'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['area', 'nombre']
        unique_together = ['area', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.area.nombre}"


class Convocatoria(models.Model):
    """
    Modelo para las convocatorias o procesos de selección
    """
    
    ESTADO_CONVOCATORIA_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('PUBLICADA', 'Publicada'),
        ('EN_PROCESO', 'En Proceso'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    TIPO_CONVOCATORIA_CHOICES = [
        ('INTERNA', 'Interna'),
        ('EXTERNA', 'Externa'),
        ('MIXTA', 'Mixta'),
    ]
    
    # Información básica
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título de la Convocatoria'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción del Puesto'
    )
    
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.CASCADE,
        related_name='convocatorias',
        verbose_name='Cargo'
    )
    
    # Fechas importantes
    fecha_apertura = models.DateTimeField(
        verbose_name='Fecha de Apertura'
    )
    
    fecha_cierre = models.DateTimeField(
        verbose_name='Fecha de Cierre'
    )
    
    fecha_inicio_trabajo = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Inicio de Trabajo'
    )
    
    # Estado y tipo
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CONVOCATORIA_CHOICES,
        default='BORRADOR',
        verbose_name='Estado'
    )
    
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CONVOCATORIA_CHOICES,
        default='EXTERNA',
        verbose_name='Tipo de Convocatoria'
    )
    
    # Requisitos
    requisitos_minimos = models.TextField(
        blank=True,
        null=True,
        verbose_name='Requisitos Mínimos'
    )
    
    requisitos_deseables = models.TextField(
        blank=True,
        null=True,
        verbose_name='Requisitos Deseables'
    )
    
    experiencia_minima = models.PositiveIntegerField(
        default=0,
        verbose_name='Experiencia Mínima (años)'
    )
    
    # Información adicional
    numero_vacantes = models.PositiveIntegerField(
        default=1,
        verbose_name='Número de Vacantes'
    )
    
    salario_ofrecido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Salario Ofrecido'
    )
    
    modalidad_trabajo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Modalidad de Trabajo'
    )
    
    ubicacion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ubicación'
    )
    
    # Responsable del proceso
    responsable_rrhh = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Responsable de RRHH'
    )
    
    # Metadatos
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Convocatoria'
        verbose_name_plural = 'Convocatorias'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['cargo']),
            models.Index(fields=['fecha_apertura', 'fecha_cierre']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.cargo.nombre}"
    
    @property
    def esta_abierta(self):
        """Verifica si la convocatoria está abierta para postulaciones"""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.estado == 'PUBLICADA' and
            self.fecha_apertura <= now <= self.fecha_cierre
        )
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes para el cierre"""
        from django.utils import timezone
        if self.estado == 'PUBLICADA':
            now = timezone.now()
            if now < self.fecha_cierre:
                delta = self.fecha_cierre - now
                return delta.days
        return 0
    
    def clean(self):
        """Validaciones del modelo"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        if self.fecha_cierre <= self.fecha_apertura:
            raise ValidationError({
                'fecha_cierre': 'La fecha de cierre debe ser posterior a la fecha de apertura.'
            })
        
        if self.fecha_inicio_trabajo and self.fecha_inicio_trabajo < timezone.now().date():
            raise ValidationError({
                'fecha_inicio_trabajo': 'La fecha de inicio de trabajo no puede ser anterior a hoy.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Postulacion(models.Model):
    """
    Modelo intermedio para manejar la relación entre Aspirante y Convocatoria
    Permite que un aspirante postule a múltiples convocatorias
    """
    
    ESTADO_POSTULACION_CHOICES = [
        ('POSTULADO', 'Postulado'),
        ('EN_REVISION', 'En Revisión'),
        ('ENTREVISTA', 'En Entrevista'),
        ('EVALUACION', 'En Evaluación'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('RETIRADO', 'Retirado'),
    ]
    
    # Relaciones principales
    aspirante = models.ForeignKey(
        'Aspirante',
        on_delete=models.CASCADE,
        related_name='postulaciones',
        verbose_name='Aspirante'
    )
    
    convocatoria = models.ForeignKey(
        Convocatoria,
        on_delete=models.CASCADE,
        related_name='postulaciones',
        verbose_name='Convocatoria'
    )
    
    # Información de la postulación
    fecha_postulacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Postulación'
    )
    
    estado_postulacion = models.CharField(
        max_length=20,
        choices=ESTADO_POSTULACION_CHOICES,
        default='POSTULADO',
        verbose_name='Estado de Postulación'
    )
    
    # Información adicional
    experiencia_anios = models.PositiveIntegerField(
        default=0,
        verbose_name='Años de Experiencia'
    )
    
    nivel_educacion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Nivel de Educación'
    )
    
    institucion_educacion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Institución de Educación'
    )
    
    cv_archivo = models.FileField(
        upload_to='cvs/',
        blank=True,
        null=True,
        verbose_name='Archivo CV'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Postulación'
        verbose_name_plural = 'Postulaciones'
        ordering = ['-fecha_postulacion']
        unique_together = ['aspirante', 'convocatoria']  # Un aspirante no puede postular dos veces a la misma convocatoria
        indexes = [
            models.Index(fields=['estado_postulacion']),
            models.Index(fields=['fecha_postulacion']),
            models.Index(fields=['aspirante', 'convocatoria']),
        ]
    
    def __str__(self):
        return f"{self.aspirante.nombre_completo} - {self.convocatoria.titulo}"
    
    @property
    def cargo_postulado(self):
        """Acceso al cargo a través de la convocatoria"""
        return self.convocatoria.cargo
    
    def clean(self):
        """Validaciones del modelo"""
        from django.core.exceptions import ValidationError
        
        # Verificar que el aspirante no haya postulado antes a la misma convocatoria
        if self.pk is None:  # Solo para nuevas postulaciones
            existing = Postulacion.objects.filter(
                aspirante=self.aspirante,
                convocatoria=self.convocatoria
            ).exists()
            if existing:
                raise ValidationError({
                    'convocatoria': 'Este aspirante ya ha postulado a esta convocatoria.'
                })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Aspirante(Persona):
    """
    Modelo para personas que pueden postular a cargos en la empresa
    Hereda todos los campos de Persona
    Las postulaciones específicas se manejan a través del modelo Postulacion
    """
    
    # Información adicional específica del aspirante
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Registro'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Aspirante'
        verbose_name_plural = 'Aspirantes'
        ordering = ['apellido_paterno', 'apellido_materno', 'nombres']
        indexes = [
            models.Index(fields=['activo']),
            models.Index(fields=['fecha_registro']),
        ]
    
    def __str__(self):
        return f"{self.nombre_completo}"
    
    @property
    def postulaciones_activas(self):
        """Obtiene las postulaciones activas del aspirante"""
        return self.postulaciones.filter(
            estado_postulacion__in=['POSTULADO', 'EN_REVISION', 'ENTREVISTA', 'EVALUACION']
        )
    
    @property
    def ultima_postulacion(self):
        """Obtiene la última postulación del aspirante"""
        return self.postulaciones.first()


class Colaborador(Persona):
    """
    Modelo para personas que trabajan en la empresa
    Hereda todos los campos de Persona
    """
    
    ESTADO_LABORAL_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('VACACIONES', 'En Vacaciones'),
        ('LICENCIA', 'En Licencia'),
        ('RENUNCIADO', 'Renunciado'),
        ('DESPEDIDO', 'Despedido'),
    ]
    
    TIPO_CONTRATO_CHOICES = [
        ('TIEMPO_COMPLETO', 'Tiempo Completo'),
        ('MEDIO_TIEMPO', 'Medio Tiempo'),
        ('POR_HORAS', 'Por Horas'),
        ('PRACTICANTE', 'Practicante'),
        ('CONSULTOR', 'Consultor'),
    ]
    
    # Información laboral específica
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.CASCADE,
        related_name='colaboradores',
        verbose_name='Cargo'
    )
    
    fecha_ingreso = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Ingreso'
    )
    
    fecha_salida = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Salida'
    )
    
    estado_laboral = models.CharField(
        max_length=20,
        choices=ESTADO_LABORAL_CHOICES,
        default='ACTIVO',
        verbose_name='Estado Laboral'
    )
    
    tipo_contrato = models.CharField(
        max_length=20,
        choices=TIPO_CONTRATO_CHOICES,
        default='TIEMPO_COMPLETO',
        verbose_name='Tipo de Contrato'
    )
    
    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Salario'
    )
    
    numero_empleado = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Número de Empleado'
    )
    
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subordinados',
        verbose_name='Supervisor'
    )
    
    # Información adicional
    fecha_ultima_evaluacion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Última Evaluación'
    )
    
    notas_laborales = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas Laborales'
    )
    
    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['-fecha_ingreso', 'apellido_paterno', 'apellido_materno']
        indexes = [
            models.Index(fields=['estado_laboral']),
            models.Index(fields=['fecha_ingreso']),
            models.Index(fields=['cargo']),
            models.Index(fields=['numero_empleado']),
        ]
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.cargo.nombre}"
    
    @property
    def antiguedad_anios(self):
        """Calcula la antigüedad en años"""
        if self.fecha_ingreso:
            today = timezone.now().date()
            return today.year - self.fecha_ingreso.year - (
                (today.month, today.day) < (self.fecha_ingreso.month, self.fecha_ingreso.day)
            )
        return None
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        from django.core.exceptions import ValidationError
        
        super().clean()  # Llamar validaciones de Persona
        
        # Validar que la fecha de ingreso no sea futura
        if self.fecha_ingreso and self.fecha_ingreso > timezone.now().date():
            raise ValidationError({
                'fecha_ingreso': 'La fecha de ingreso no puede ser futura.'
            })
        
        # Validar que la fecha de salida sea posterior a la fecha de ingreso
        if self.fecha_salida and self.fecha_ingreso and self.fecha_salida <= self.fecha_ingreso:
            raise ValidationError({
                'fecha_salida': 'La fecha de salida debe ser posterior a la fecha de ingreso.'
            })
        
        # Validar que no sea su propio supervisor
        if self.supervisor and self.supervisor.id == self.id:
            raise ValidationError({
                'supervisor': 'Una persona no puede ser su propio supervisor.'
            })


# =============================================================================
# MODELOS PARA CURRICULUM VITAE (CV)
# =============================================================================

class FormacionAcademica(models.Model):
    """
    Modelo para la formación académica de aspirantes y colaboradores
    """
    
    GRADO_CHOICES = [
        ('BACHILLER', 'Bachiller'),
        ('TECNICO', 'Técnico'),
        ('TECNICO_SUPERIOR', 'Técnico Superior'),
        ('LICENCIADO', 'Licenciado'),
        ('INGENIERO', 'Ingeniero'),
        ('MAESTRO', 'Maestro'),
        ('DOCTOR', 'Doctor'),
        ('POSTGRADO', 'Postgrado'),
        ('DIPLOMADO', 'Diplomado'),
        ('CERTIFICACION', 'Certificación'),
    ]
    
    # Relaciones - puede pertenecer a un aspirante o colaborador
    aspirante = models.ForeignKey(
        Aspirante,
        on_delete=models.CASCADE,
        related_name='formaciones_academicas',
        blank=True,
        null=True,
        verbose_name='Aspirante'
    )
    
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name='formaciones_academicas',
        blank=True,
        null=True,
        verbose_name='Colaborador'
    )
    
    # Información académica
    grado = models.CharField(
        max_length=30,
        choices=GRADO_CHOICES,
        verbose_name='Grado'
    )
    
    especialidad = models.CharField(
        max_length=200,
        verbose_name='Especialidad'
    )
    
    centro_estudio = models.CharField(
        max_length=200,
        verbose_name='Centro de Estudio'
    )
    
    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad'
    )
    
    pais = models.CharField(
        max_length=100,
        verbose_name='País'
    )
    
    # Fechas
    fecha_expedicion = models.DateField(
        verbose_name='Fecha de Expedición'
    )
    
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    
    # Información adicional
    promedio = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Promedio'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Formación Académica'
        verbose_name_plural = 'Formaciones Académicas'
        ordering = ['-fecha_expedicion']
        indexes = [
            models.Index(fields=['aspirante']),
            models.Index(fields=['colaborador']),
            models.Index(fields=['grado']),
        ]
    
    def __str__(self):
        persona = self.aspirante if self.aspirante else self.colaborador
        return f"{persona.nombre_completo} - {self.grado} en {self.especialidad}"
    
    def clean(self):
        """Validaciones del modelo"""
        from django.core.exceptions import ValidationError
        
        # Verificar que tenga al menos un aspirante o colaborador
        if not self.aspirante and not self.colaborador:
            raise ValidationError({
                'aspirante': 'Debe especificar un aspirante o colaborador.'
            })
        
        if self.aspirante and self.colaborador:
            raise ValidationError({
                'aspirante': 'No puede especificar tanto un aspirante como un colaborador.'
            })
        
        # Validar fechas
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        if self.fecha_expedicion < self.fecha_fin:
            raise ValidationError({
                'fecha_expedicion': 'La fecha de expedición no puede ser anterior a la fecha de fin.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class CursoEspecializacion(models.Model):
    """
    Modelo para cursos y programas de especialización de aspirantes y colaboradores
    """
    
    TIPO_ESTUDIO_CHOICES = [
        ('CURSO', 'Curso'),
        ('DIPLOMADO', 'Diplomado'),
        ('CERTIFICACION', 'Certificación'),
        ('ESPECIALIZACION', 'Especialización'),
        ('MAESTRIA', 'Maestría'),
        ('DOCTORADO', 'Doctorado'),
        ('TALLER', 'Taller'),
        ('SEMINARIO', 'Seminario'),
        ('CONGRESO', 'Congreso'),
        ('CONFERENCIA', 'Conferencia'),
    ]
    
    NIVEL_CHOICES = [
        ('BASICO', 'Básico'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
        ('EXPERTO', 'Experto'),
    ]
    
    # Relaciones - puede pertenecer a un aspirante o colaborador
    aspirante = models.ForeignKey(
        Aspirante,
        on_delete=models.CASCADE,
        related_name='cursos_especializacion',
        blank=True,
        null=True,
        verbose_name='Aspirante'
    )
    
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name='cursos_especializacion',
        blank=True,
        null=True,
        verbose_name='Colaborador'
    )
    
    # Información del curso
    tipo_estudio = models.CharField(
        max_length=20,
        choices=TIPO_ESTUDIO_CHOICES,
        verbose_name='Tipo de Estudio'
    )
    
    descripcion = models.CharField(
        max_length=300,
        verbose_name='Descripción'
    )
    
    institucion = models.CharField(
        max_length=200,
        verbose_name='Institución'
    )
    
    pais = models.CharField(
        max_length=100,
        verbose_name='País'
    )
    
    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad'
    )
    
    # Fechas
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    
    # Información adicional
    horas_lectivas = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Horas Lectivas'
    )
    
    nivel = models.CharField(
        max_length=15,
        choices=NIVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name='Nivel'
    )
    
    certificado = models.FileField(
        upload_to='certificados/',
        blank=True,
        null=True,
        verbose_name='Certificado'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Curso de Especialización'
        verbose_name_plural = 'Cursos de Especialización'
        ordering = ['-fecha_fin']
        indexes = [
            models.Index(fields=['aspirante']),
            models.Index(fields=['colaborador']),
            models.Index(fields=['tipo_estudio']),
        ]
    
    def __str__(self):
        persona = self.aspirante if self.aspirante else self.colaborador
        return f"{persona.nombre_completo} - {self.tipo_estudio}: {self.descripcion}"
    
    def clean(self):
        """Validaciones del modelo"""
        from django.core.exceptions import ValidationError
        
        # Verificar que tenga al menos un aspirante o colaborador
        if not self.aspirante and not self.colaborador:
            raise ValidationError({
                'aspirante': 'Debe especificar un aspirante o colaborador.'
            })
        
        if self.aspirante and self.colaborador:
            raise ValidationError({
                'aspirante': 'No puede especificar tanto un aspirante como un colaborador.'
            })
        
        # Validar fechas
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ExperienciaLaboral(models.Model):
    """
    Modelo para la experiencia laboral de aspirantes y colaboradores
    """
    
    TIPO_EXPERIENCIA_CHOICES = [
        ('GENERAL', 'General'),
        ('ESPECIFICA', 'Específica'),
        ('LIDERAZGO', 'Liderazgo'),
        ('TECNICA', 'Técnica'),
        ('ADMINISTRATIVA', 'Administrativa'),
        ('VENTAS', 'Ventas'),
        ('ATENCION_CLIENTE', 'Atención al Cliente'),
        ('INVESTIGACION', 'Investigación'),
        ('DOCENCIA', 'Docencia'),
    ]
    
    TIPO_ENTIDAD_CHOICES = [
        ('PUBLICO', 'Público'),
        ('PRIVADO', 'Privado'),
        ('ONG', 'ONG'),
        ('INTERNACIONAL', 'Internacional'),
        ('MIXTO', 'Mixto'),
    ]
    
    # Relaciones - puede pertenecer a un aspirante o colaborador
    aspirante = models.ForeignKey(
        Aspirante,
        on_delete=models.CASCADE,
        related_name='experiencias_laborales',
        blank=True,
        null=True,
        verbose_name='Aspirante'
    )
    
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        related_name='experiencias_laborales',
        blank=True,
        null=True,
        verbose_name='Colaborador'
    )
    
    # Información laboral
    tipo_experiencia = models.CharField(
        max_length=20,
        choices=TIPO_EXPERIENCIA_CHOICES,
        verbose_name='Tipo de Experiencia'
    )
    
    tipo_entidad = models.CharField(
        max_length=15,
        choices=TIPO_ENTIDAD_CHOICES,
        verbose_name='Tipo de Entidad'
    )
    
    nombre_entidad = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Entidad'
    )
    
    cargo = models.CharField(
        max_length=150,
        verbose_name='Cargo'
    )
    
    # Fechas
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Fin'
    )
    
    # Información adicional
    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Salario'
    )
    
    motivo_salida = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Motivo de Salida'
    )
    
    logros = models.TextField(
        blank=True,
        null=True,
        verbose_name='Logros Principales'
    )
    
    responsabilidades = models.TextField(
        blank=True,
        null=True,
        verbose_name='Responsabilidades'
    )
    
    supervisor = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Supervisor'
    )
    
    telefono_referencia = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Teléfono de Referencia'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Experiencia Laboral'
        verbose_name_plural = 'Experiencias Laborales'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['aspirante']),
            models.Index(fields=['colaborador']),
            models.Index(fields=['tipo_experiencia']),
            models.Index(fields=['fecha_inicio']),
        ]
    
    def __str__(self):
        persona = self.aspirante if self.aspirante else self.colaborador
        return f"{persona.nombre_completo} - {self.cargo} en {self.nombre_entidad}"
    
    @property
    def duracion_meses(self):
        """Calcula la duración en meses"""
        if self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            return delta.days // 30
        else:
            from django.utils import timezone
            delta = timezone.now().date() - self.fecha_inicio
            return delta.days // 30
    
    @property
    def esta_activa(self):
        """Verifica si la experiencia está activa (sin fecha de fin)"""
        return self.fecha_fin is None
    
    def clean(self):
        """Validaciones del modelo"""
        from django.core.exceptions import ValidationError
        
        # Verificar que tenga al menos un aspirante o colaborador
        if not self.aspirante and not self.colaborador:
            raise ValidationError({
                'aspirante': 'Debe especificar un aspirante o colaborador.'
            })
        
        if self.aspirante and self.colaborador:
            raise ValidationError({
                'aspirante': 'No puede especificar tanto un aspirante como un colaborador.'
            })
        
        # Validar fechas
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)