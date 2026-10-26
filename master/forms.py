from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q

from .models import (
    Postulacion, Convocatoria, FormacionAcademica, CursoEspecializacion,
    ExperienciaLaboral, Persona, CV, Colaborador, ContratoColaborador, PerfilAcceso,
    ActividadSemanal, Proyecto, AsignacionProyecto, Skill, CursoAprendizaje,
    RutaInduccion, RutaInduccionCurso, AsignacionCurso, Cargo,
)
from .proyecto_matching import parse_skills_texto
from .actividades_catalogo import GRUPO_CHOICES, TIPOS_POR_GRUPO, tipo_pertenece_a_grupo
from .permissions import MODULOS_MENU


def validar_archivo_pdf(archivo):
    """Acepta solo PDF. Devuelve el archivo o None; lanza ValueError si no es PDF."""
    if not archivo:
        return None
    nombre = (getattr(archivo, 'name', '') or '').lower()
    if not nombre.endswith('.pdf'):
        raise ValueError('Solo se permiten archivos PDF.')
    content_type = (getattr(archivo, 'content_type', '') or '').lower()
    if content_type and content_type not in (
        'application/pdf',
        'application/x-pdf',
        'application/octet-stream',
    ):
        raise ValueError('Solo se permiten archivos PDF.')
    return archivo


class PasswordChangeSpanishForm(PasswordChangeForm):
    """Formulario para cambiar contraseña con etiquetas en español."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Contraseña actual'
        self.fields['new_password1'].label = 'Nueva contraseña'
        self.fields['new_password2'].label = 'Confirmar nueva contraseña'
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off',
            })
        self.fields['old_password'].widget.attrs['autocomplete'] = 'current-password'
        self.fields['new_password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['new_password2'].widget.attrs['autocomplete'] = 'new-password'

class CustomLoginForm(AuthenticationForm):
    """Formulario personalizado de login"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autocomplete': 'username',
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',

        }),
        label='Contraseña'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'custom-control-input',
        }),
        label='Recordarme'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error
        self.fields['username'].error_messages = {
            'required': 'El campo usuario es obligatorio.',
            'invalid': 'Ingrese un nombre de usuario válido.',
        }
        self.fields['password'].error_messages = {
            'required': 'El campo contraseña es obligatorio.',
        }
    
    def confirm_login_allowed(self, user):
        """Personalizar el mensaje de error de autenticación"""
        if not user.is_active:
            raise forms.ValidationError(
                'Esta cuenta está desactivada.',
                code='inactive',
            )
        super().confirm_login_allowed(user)
    
    def get_invalid_login_error(self):
        """Personalizar el mensaje de error de login inválido"""
        return forms.ValidationError(
            'Por favor, ingrese un nombre de usuario y contraseña correctos. '
            'Tenga en cuenta que ambos campos pueden distinguir entre mayúsculas y minúsculas.',
            code='invalid_login',
        )


class PostulacionForm(forms.ModelForm):
    """Formulario para editar postulaciones"""
    
    class Meta:
        model = Postulacion
        fields = [
            'convocatoria', 'estado_postulacion', 'experiencia_anios', 'nivel_educacion',
            'institucion_educacion', 'observaciones'
        ]
        widgets = {
            'convocatoria': forms.Select(attrs={'class': 'form-control'}),
            'estado_postulacion': forms.Select(attrs={'class': 'form-control'}),
            'experiencia_anios': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'nivel_educacion': forms.TextInput(attrs={'class': 'form-control'}),
            'institucion_educacion': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'convocatoria': 'Convocatoria',
            'estado_postulacion': 'Estado de Postulación',
            'experiencia_anios': 'Años de Experiencia',
            'nivel_educacion': 'Nivel de Educación',
            'institucion_educacion': 'Institución de Educación',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar convocatorias activas
        self.fields['convocatoria'].queryset = Convocatoria.objects.filter(activo=True).select_related('cargo__area')


class CVPerfilForm(forms.ModelForm):
    """Formulario para editar el perfil profesional (CV) de una persona."""

    class Meta:
        model = CV
        fields = [
            'resumen_profesional', 'objetivo_profesional',
            'email_profesional', 'telefono_profesional',
            'linkedin', 'portfolio', 'cv_archivo', 'cv_archivo_anexos',
        ]
        widgets = {
            'resumen_profesional': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objetivo_profesional': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'email_profesional': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_profesional': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'portfolio': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'cv_archivo': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'application/pdf,.pdf'}),
            'cv_archivo_anexos': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'application/pdf,.pdf'}),
        }
        labels = {
            'cv_archivo': 'CV descriptivo (PDF)',
            'cv_archivo_anexos': 'CV con anexos (PDF)',
        }

    def clean_cv_archivo(self):
        try:
            return validar_archivo_pdf(self.cleaned_data.get('cv_archivo'))
        except ValueError as exc:
            raise forms.ValidationError(str(exc))

    def clean_cv_archivo_anexos(self):
        try:
            return validar_archivo_pdf(self.cleaned_data.get('cv_archivo_anexos'))
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class PersonaEditForm(forms.ModelForm):
    """Formulario Bootstrap para editar una persona"""

    foto_perfil = forms.ImageField(
        label='Foto de perfil',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/jpeg,image/png,image/webp,image/gif',
        }),
    )

    class Meta:
        model = Persona
        fields = [
            'tipo_documento', 'numero_documento', 'apellido_paterno', 'apellido_materno',
            'nombres', 'fecha_nacimiento', 'sexo', 'estado_civil', 'celular', 'email',
            'direccion', 'distrito', 'provincia', 'departamento',
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'custom-select form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'},
            ),
            'sexo': forms.Select(attrs={'class': 'custom-select form-control'}),
            'estado_civil': forms.Select(attrs={'class': 'custom-select form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'departamento': forms.Select(attrs={'class': 'custom-select form-control'}),
            'provincia': forms.Select(attrs={'class': 'custom-select form-control'}),
            'distrito': forms.Select(attrs={'class': 'custom-select form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.cv = kwargs.pop('cv', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        persona = super().save(commit=commit)
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            cv, _created = CV.objects.get_or_create(persona=persona)
            cv.foto_perfil = foto
            cv.save(update_fields=['foto_perfil'])
        return persona


class PersonaAltaForm(forms.ModelForm):
    """Formulario para dar de alta una persona (creación / modal nuevo empleado)."""

    class Meta:
        model = Persona
        fields = [
            'tipo_documento', 'numero_documento', 'apellido_paterno', 'apellido_materno',
            'nombres', 'fecha_nacimiento', 'sexo', 'estado_civil', 'celular', 'email',
            'direccion', 'distrito', 'provincia', 'departamento',
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'custom-select form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'},
            ),
            'sexo': forms.Select(attrs={'class': 'custom-select form-control'}),
            'estado_civil': forms.Select(attrs={'class': 'custom-select form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'departamento': forms.Select(attrs={'class': 'custom-select form-control'}),
            'provincia': forms.Select(attrs={'class': 'custom-select form-control'}),
            'distrito': forms.Select(attrs={'class': 'custom-select form-control'}),
        }


class PersonaCreateForm(forms.ModelForm):
    """Formulario para crear una nueva persona con su postulación"""
    
    class Meta:
        model = Postulacion
        fields = [
            'convocatoria', 'estado_postulacion', 'experiencia_anios', 'nivel_educacion',
            'institucion_educacion', 'observaciones'
        ]
        widgets = {
            'convocatoria': forms.Select(attrs={'class': 'form-control'}),
            'estado_postulacion': forms.Select(attrs={'class': 'form-control'}),
            'experiencia_anios': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'nivel_educacion': forms.TextInput(attrs={'class': 'form-control'}),
            'institucion_educacion': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'convocatoria': 'Convocatoria *',
            'estado_postulacion': 'Estado de Postulación *',
            'experiencia_anios': 'Años de Experiencia',
            'nivel_educacion': 'Nivel de Educación',
            'institucion_educacion': 'Institución de Educación',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer valor por defecto para estado de postulación
        self.fields['estado_postulacion'].initial = 'POSTULADO'
        # Filtrar convocatorias activas
        self.fields['convocatoria'].queryset = Convocatoria.objects.filter(activo=True).select_related('cargo__area')
    
    def clean(self):
        cleaned_data = super().clean()
        numero_documento = cleaned_data.get('numero_documento')
        email = cleaned_data.get('email')
        
        # Verificar si ya existe una persona con el mismo documento
        if numero_documento:
            if Persona.objects.filter(numero_documento=numero_documento).exists():
                raise forms.ValidationError("Ya existe una persona con este número de documento.")
        
        # Verificar si ya existe una persona con el mismo email
        if email:
            if Persona.objects.filter(email=email).exists():
                raise forms.ValidationError("Ya existe una persona con este email.")
        
        return cleaned_data
    
    def save(self, commit=True):
        # Crear la persona primero
        persona = Persona.objects.create(
            nombres=self.cleaned_data['nombres'],
            apellido_paterno=self.cleaned_data['apellido_paterno'],
            apellido_materno=self.cleaned_data['apellido_materno'],
            numero_documento=self.cleaned_data['numero_documento'],
            tipo_documento=self.cleaned_data['tipo_documento'],
            email=self.cleaned_data['email'],
            celular=self.cleaned_data.get('celular', ''),
            fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
            sexo=self.cleaned_data['sexo'],
            estado_civil=self.cleaned_data['estado_civil']
        )
        
        # Crear el CV para la persona
        cv = CV.objects.create(persona=persona)
        
        # Crear la postulación
        postulacion = super().save(commit=False)
        postulacion.persona = persona
        if commit:
            postulacion.save()
        return postulacion


class FormacionAcademicaForm(forms.ModelForm):
    """Formulario para formación académica"""
    
    class Meta:
        model = FormacionAcademica
        fields = [
            'grado', 'especialidad', 'centro_estudio', 'ciudad', 'pais',
            'fecha_expedicion', 'fecha_inicio', 'fecha_fin', 'promedio', 'observaciones',
            'archivo', 'cv'
        ]
        widgets = {
            'grado': forms.Select(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'centro_estudio': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_expedicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'promedio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '20'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf,.pdf'}),
            'cv': forms.HiddenInput(),
        }
        labels = {
            'grado': 'Grado',
            'especialidad': 'Especialidad',
            'centro_estudio': 'Centro de Estudio',
            'ciudad': 'Ciudad',
            'pais': 'País',
            'fecha_expedicion': 'Fecha de Expedición',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'promedio': 'Promedio',
            'observaciones': 'Observaciones',
            'archivo': 'Archivo (PDF)',
        }

    def clean_archivo(self):
        try:
            return validar_archivo_pdf(self.cleaned_data.get('archivo'))
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class CursoEspecializacionForm(forms.ModelForm):
    """Formulario para cursos de especialización"""
    
    class Meta:
        model = CursoEspecializacion
        fields = [
            'tipo_estudio', 'descripcion', 'institucion', 'pais', 'ciudad',
            'fecha_inicio', 'fecha_fin', 'horas_lectivas', 'nivel', 'certificado', 'observaciones',
            'cv'
        ]
        widgets = {
            'tipo_estudio': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horas_lectivas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'certificado': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf,.pdf'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cv': forms.HiddenInput(),
        }
        labels = {
            'tipo_estudio': 'Tipo de Estudio',
            'descripcion': 'Descripción',
            'institucion': 'Institución',
            'pais': 'País',
            'ciudad': 'Ciudad',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'horas_lectivas': 'Horas Lectivas',
            'nivel': 'Nivel',
            'certificado': 'Certificado (PDF)',
            'observaciones': 'Observaciones',
        }

    def clean_certificado(self):
        try:
            return validar_archivo_pdf(self.cleaned_data.get('certificado'))
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class ExperienciaLaboralForm(forms.ModelForm):
    """Formulario para experiencia laboral"""
    
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'tipo_experiencia', 'tipo_entidad', 'nombre_entidad', 'cargo',
            'fecha_inicio', 'fecha_fin', 'salario', 'motivo_salida', 'logros',
            'responsabilidades', 'supervisor', 'telefono_referencia', 'observaciones',
            'archivo', 'cv'
        ]
        widgets = {
            'tipo_experiencia': forms.Select(attrs={'class': 'form-control'}),
            'tipo_entidad': forms.Select(attrs={'class': 'form-control'}),
            'nombre_entidad': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'motivo_salida': forms.Select(attrs={'class': 'form-control'}),
            'logros': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsabilidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supervisor': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf,.pdf'}),
            'cv': forms.HiddenInput(),
        }
        labels = {
            'tipo_experiencia': 'Tipo de Experiencia',
            'tipo_entidad': 'Tipo de Entidad',
            'nombre_entidad': 'Nombre de la Entidad',
            'cargo': 'Cargo',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'salario': 'Salario',
            'motivo_salida': 'Motivo de Salida',
            'logros': 'Logros Principales',
            'responsabilidades': 'Responsabilidades',
            'supervisor': 'Supervisor',
            'telefono_referencia': 'Teléfono de Referencia',
            'observaciones': 'Observaciones',
            'archivo': 'Archivo (PDF)',
        }

    def clean_archivo(self):
        try:
            return validar_archivo_pdf(self.cleaned_data.get('archivo'))
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class ColaboradorForm(forms.ModelForm):
    """
    Formulario para crear un colaborador desde una postulación aprobada
    """
    
    class Meta:
        model = Colaborador
        fields = [
            'cargo', 'fecha_ingreso', 'estado_laboral', 'tipo_contrato', 
            'salario', 'numero_empleado', 'supervisor'
        ]
        widgets = {
            'cargo': forms.Select(attrs={'class': 'custom-select form-control'}),
            'supervisor': forms.Select(attrs={'class': 'custom-select form-control'}),
            'estado_laboral': forms.Select(attrs={'class': 'custom-select form-control'}),
            'tipo_contrato': forms.Select(attrs={'class': 'custom-select form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'salario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'numero_empleado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: EMP001',
            }),
        }
        labels = {
            'cargo': 'Cargo *',
            'fecha_ingreso': 'Fecha de Ingreso *',
            'estado_laboral': 'Estado Laboral *',
            'tipo_contrato': 'Tipo de Contrato *',
            'salario': 'Salario',
            'numero_empleado': 'Número de Empleado',
            'supervisor': 'Supervisor',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que el cargo sea requerido
        self.fields['cargo'].required = True
        self.fields['fecha_ingreso'].required = True
        self.fields['estado_laboral'].required = True
        self.fields['tipo_contrato'].required = True
        
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if field_name not in ['cargo', 'supervisor']:
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_numero_empleado(self):
        """
        Validar que el número de empleado sea único
        """
        numero_empleado = self.cleaned_data.get('numero_empleado')
        if numero_empleado:
            qs = Colaborador.objects.filter(numero_empleado=numero_empleado)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este número de empleado ya existe.')
        return numero_empleado


class ContratoColaboradorForm(forms.ModelForm):
    """Formulario para registrar un contrato laboral con archivo PDF."""

    class Meta:
        model = ContratoColaborador
        fields = ['tipo_contrato', 'fecha_inicio', 'fecha_fin', 'archivo', 'observaciones']
        widgets = {
            'tipo_contrato': forms.Select(attrs={'class': 'custom-select form-control'}),
            'fecha_inicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'},
            ),
            'fecha_fin': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'},
            ),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'application/pdf,.pdf',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Opcional',
            }),
        }
        labels = {
            'tipo_contrato': 'Tipo de contrato *',
            'fecha_inicio': 'Fecha de inicio *',
            'fecha_fin': 'Fecha de fin',
            'archivo': 'Archivo PDF (opcional)',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_fin'].required = False
        self.fields['observaciones'].required = False
        self.fields['archivo'].required = False

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            nombre = archivo.name.lower()
            if not nombre.endswith('.pdf'):
                raise forms.ValidationError('Solo se permiten archivos PDF.')
        return archivo


MODULO_FORM_CHOICES = [(m['clave'], m['label']) for m in MODULOS_MENU]


class UsuarioAccesoForm(forms.Form):
    """Alta y edición de usuarios del sistema con módulos asignables."""

    username = forms.CharField(
        max_length=150,
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='Nombres',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Apellidos',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        required=False,
        label='Correo',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        required=False,
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        required=False,
    )
    es_administrador = forms.BooleanField(
        required=False,
        label='Administrador (acceso total)',
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
    )
    modulos = forms.MultipleChoiceField(
        choices=MODULO_FORM_CHOICES,
        required=False,
        label='Módulos permitidos',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Usuario activo',
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
    )
    persona_vinculada = forms.ModelChoiceField(
        queryset=Persona.objects.none(),
        required=False,
        label='Empleado vinculado',
        empty_label='— Sin vincular —',
        widget=forms.Select(attrs={'class': 'form-control custom-select'}),
        help_text='Vincula esta cuenta al registro del empleado para que vea su perfil personal.',
    )

    def __init__(self, *args, user_instance=None, **kwargs):
        self.user_instance = user_instance
        super().__init__(*args, **kwargs)
        is_edit = user_instance is not None

        empleados_qs = Persona.objects.filter(
            colaborador__isnull=False,
        ).select_related('colaborador').order_by('apellido_paterno', 'nombres')
        if is_edit:
            empleados_qs = empleados_qs.filter(
                Q(user__isnull=True) | Q(user=user_instance),
            )
            persona = getattr(user_instance, 'perfil', None)
            if persona:
                self.initial['persona_vinculada'] = persona.pk
        else:
            empleados_qs = empleados_qs.filter(user__isnull=True)
        self.fields['persona_vinculada'].queryset = empleados_qs

        if is_edit:
            self.fields['username'].disabled = True
            perfil = getattr(user_instance, 'perfil_acceso', None)
            self.initial.update({
                'username': user_instance.username,
                'first_name': user_instance.first_name,
                'last_name': user_instance.last_name,
                'email': user_instance.email,
                'es_administrador': perfil.es_administrador if perfil else False,
                'modulos': perfil.modulos if perfil else [],
                'is_active': user_instance.is_active,
            })
            self.fields['password1'].label = 'Nueva contraseña (opcional)'
            self.fields['password2'].label = 'Confirmar nueva contraseña'
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            del self.fields['is_active']

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.user_instance is None:
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean(self):
        cleaned = super().clean()
        es_admin = cleaned.get('es_administrador')
        modulos = cleaned.get('modulos') or []
        persona = cleaned.get('persona_vinculada')
        if not persona and self.user_instance:
            persona = getattr(self.user_instance, 'perfil', None)
        if not es_admin and not modulos and not persona:
            raise forms.ValidationError(
                'Debe asignar al menos un módulo, marcar al usuario como administrador '
                'o vincular un empleado.'
            )
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
            elif p1:
                password_validation.validate_password(p1)
        elif self.user_instance is None:
            self.add_error('password1', 'La contraseña es obligatoria al crear un usuario.')
        return cleaned

    def _count_other_admins(self, exclude_user_id=None):
        qs = PerfilAcceso.objects.filter(es_administrador=True)
        if exclude_user_id:
            qs = qs.exclude(user_id=exclude_user_id)
        return qs.count()

    def clean_es_administrador(self):
        es_admin = self.cleaned_data.get('es_administrador')
        if self.user_instance and not es_admin:
            perfil = getattr(self.user_instance, 'perfil_acceso', None)
            if perfil and perfil.es_administrador and self._count_other_admins(self.user_instance.pk) == 0:
                raise forms.ValidationError(
                    'No puede quitar el rol de administrador al último administrador del sistema.'
                )
        return es_admin

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active', True)
        if self.user_instance and not is_active:
            perfil = getattr(self.user_instance, 'perfil_acceso', None)
            if perfil and perfil.es_administrador and self._count_other_admins(self.user_instance.pk) == 0:
                raise forms.ValidationError(
                    'No puede desactivar al último administrador del sistema.'
                )
        return is_active

    def _sync_persona_link(self, user):
        """Vincula o desvincula la cuenta con un registro Persona (empleado)."""
        persona_nueva = self.cleaned_data.get('persona_vinculada')
        Persona.objects.filter(user=user).update(user=None)
        if persona_nueva:
            Persona.objects.filter(pk=persona_nueva.pk).update(user=None)
            persona_nueva.user = user
            persona_nueva.save(update_fields=['user'])

    def save(self):
        es_admin = self.cleaned_data['es_administrador']
        modulos = list(self.cleaned_data.get('modulos') or [])
        if es_admin:
            modulos = []

        if self.user_instance is None:
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1'],
                email=self.cleaned_data.get('email') or '',
                first_name=self.cleaned_data.get('first_name') or '',
                last_name=self.cleaned_data.get('last_name') or '',
            )
            PerfilAcceso.objects.create(
                user=user,
                es_administrador=es_admin,
                modulos=modulos,
            )
            self._sync_persona_link(user)
            return user

        user = self.user_instance
        user.first_name = self.cleaned_data.get('first_name') or ''
        user.last_name = self.cleaned_data.get('last_name') or ''
        user.email = self.cleaned_data.get('email') or ''
        user.is_active = self.cleaned_data.get('is_active', True)
        user.save()

        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])

        perfil, _ = PerfilAcceso.objects.get_or_create(
            user=user,
            defaults={'es_administrador': es_admin, 'modulos': modulos},
        )
        perfil.es_administrador = es_admin
        perfil.modulos = modulos
        perfil.save()
        self._sync_persona_link(user)
        return user


class ActividadSemanalForm(forms.ModelForm):
    """Formulario para registrar una actividad semanal."""

    class Meta:
        model = ActividadSemanal
        fields = ['grupo', 'tipo', 'fecha', 'descripcion', 'cliente_proyecto', 'registro']
        widgets = {
            'grupo': forms.Select(attrs={'class': 'custom-select form-control', 'id': 'id_grupo'}),
            'tipo': forms.Select(attrs={'class': 'custom-select form-control', 'id': 'id_tipo'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cliente_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'registro': forms.HiddenInput(),
        }
        labels = {
            'grupo': 'Grupo',
            'tipo': 'Tipo de actividad',
            'fecha': 'Fecha',
            'descripcion': 'Descripción',
            'cliente_proyecto': 'Cliente o proyecto',
        }

    def __init__(self, *args, **kwargs):
        self.registro = kwargs.pop('registro', None)
        super().__init__(*args, **kwargs)
        # Choices desde el catálogo (no desde BD): requiere el .py desplegado + reinicio
        self.fields['grupo'].choices = [('', '---------')] + list(GRUPO_CHOICES)
        self.fields['tipo'].choices = [('', '---------')]
        grupo = self.data.get('grupo') if self.data else None
        if not grupo and self.instance.pk:
            grupo = self.instance.grupo
        if not grupo:
            grupo = self.initial.get('grupo')
        if grupo:
            self.fields['tipo'].choices = [('', '---------')] + list(TIPOS_POR_GRUPO.get(grupo, []))
        if self.registro:
            self.fields['registro'].initial = self.registro.pk
            self.fields['fecha'].widget.attrs['min'] = self.registro.fecha_inicio.isoformat()
            self.fields['fecha'].widget.attrs['max'] = self.registro.fecha_fin.isoformat()

    def clean(self):
        cleaned_data = super().clean()
        grupo = cleaned_data.get('grupo')
        tipo = cleaned_data.get('tipo')
        fecha = cleaned_data.get('fecha')
        registro = cleaned_data.get('registro') or self.registro

        if grupo and tipo and not tipo_pertenece_a_grupo(grupo, tipo):
            self.add_error('tipo', 'El tipo seleccionado no corresponde al grupo indicado.')

        if registro and fecha:
            if fecha < registro.fecha_inicio or fecha > registro.fecha_fin:
                self.add_error(
                    'fecha',
                    f'La fecha debe estar entre {registro.fecha_inicio.strftime("%d/%m/%Y")} '
                    f'y {registro.fecha_fin.strftime("%d/%m/%Y")}.',
                )

        return cleaned_data


class ProyectoForm(forms.ModelForm):
    skills_texto = forms.CharField(
        required=False,
        label='Skills / características requeridas',
        help_text='Separe por comas. Ej: Python, Django, React, liderazgo',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Python, Django, SQL, comunicación...',
        }),
    )

    class Meta:
        model = Proyecto
        fields = [
            'nombre', 'cliente', 'descripcion', 'estado',
            'fecha_inicio', 'fecha_fin', 'horas_estimadas',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proyecto'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cliente u organización'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado': forms.Select(attrs={'class': 'custom-select form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horas_estimadas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].required = True
        if self.instance and self.instance.pk:
            nombres = list(
                self.instance.skills.order_by('nombre').values_list('nombre', flat=True)
            )
            self.fields['skills_texto'].initial = ', '.join(nombres)

    def sync_skills(self, proyecto):
        from .models import ProyectoSkill

        nombres = parse_skills_texto(self.cleaned_data.get('skills_texto'))
        proyecto.proyecto_skills.all().delete()
        for nombre in nombres:
            skill = Skill.objects.filter(nombre__iexact=nombre).first()
            if not skill:
                skill = Skill.objects.create(nombre=nombre, tipo='TECNICA')
            ProyectoSkill.objects.create(proyecto=proyecto, skill=skill, peso=1)


class AsignacionProyectoForm(forms.ModelForm):
    class Meta:
        model = AsignacionProyecto
        fields = [
            'colaborador', 'rol', 'horas_semanales',
            'fecha_inicio', 'fecha_fin', 'activo', 'notas',
        ]
        widgets = {
            'colaborador': forms.Select(attrs={'class': 'custom-select form-control'}),
            'rol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Backend, Lead, QA'}),
            'horas_semanales': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '60'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        proyecto = kwargs.pop('proyecto', None)
        super().__init__(*args, **kwargs)
        qs = Colaborador.objects.filter(
            estado_laboral='ACTIVO', persona__isnull=False
        ).select_related('persona', 'cargo').order_by(
            'persona__apellido_paterno', 'persona__nombres'
        )
        if proyecto:
            ya_ids = list(proyecto.asignaciones.values_list('colaborador_id', flat=True))
            if self.instance and self.instance.colaborador_id:
                ya_ids = [i for i in ya_ids if i != self.instance.colaborador_id]
            qs = qs.exclude(id__in=ya_ids)
        self.fields['colaborador'].queryset = qs
        self.fields['colaborador'].label_from_instance = (
            lambda obj: f'{obj.persona.nombre_completo} — {obj.cargo.nombre}'
            if obj.persona_id and obj.cargo_id else str(obj)
        )
        self.fields['horas_semanales'].required = True
        self.fields['colaborador'].required = True


class CursoAprendizajeForm(forms.ModelForm):
    cargos = forms.ModelMultipleChoiceField(
        queryset=Cargo.objects.filter(activo=True).select_related('area').order_by('area__nombre', 'nombre'),
        required=False,
        label='Cargos visibles',
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'}),
        help_text='Solo aplica si el alcance es “Solo cargos seleccionados”.',
    )

    class Meta:
        model = CursoAprendizaje
        fields = [
            'nombre', 'descripcion', 'enlace_evaluacion', 'nota_minima',
            'alcance', 'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'enlace_evaluacion': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://forms.google.com/...'}),
            'nota_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '20', 'step': '0.01'}),
            'alcance': forms.Select(attrs={'class': 'custom-select form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

    def __init__(self, *args, tipo_fijo='INDUCCION', **kwargs):
        self.tipo_fijo = tipo_fijo if tipo_fijo in ('INDUCCION', 'CAPACITACION') else 'INDUCCION'
        super().__init__(*args, **kwargs)
        self.fields['cargos'].label_from_instance = (
            lambda c: f'{c.area.nombre} — {c.nombre}' if c.area_id else c.nombre
        )
        # Alcance solo aplica a capacitaciones libres
        if self.tipo_fijo == 'INDUCCION':
            self.fields['alcance'].initial = 'TODOS'
            self.fields['alcance'].widget = forms.HiddenInput()
            self.fields['cargos'].widget = forms.MultipleHiddenInput()
        if self.instance and self.instance.pk:
            self.fields['cargos'].initial = self.instance.cargos_visibles.all()

    def recursos_iniciales(self):
        """Lista de {titulo, url} para la UI de cajitas (POST o instancia)."""
        if self.is_bound and hasattr(self.data, 'getlist'):
            titulos = self.data.getlist('recurso_titulo')
            urls = self.data.getlist('recurso_url')
            items = []
            for i, url in enumerate(urls):
                titulo = titulos[i] if i < len(titulos) else ''
                if (url or '').strip() or (titulo or '').strip():
                    items.append({'titulo': (titulo or '').strip(), 'url': (url or '').strip()})
            return items or [{'titulo': '', 'url': ''}]
        recursos = []
        if self.instance and self.instance.pk:
            for r in self.instance.recursos or []:
                url = (r.get('url') or '').strip()
                if url:
                    recursos.append({
                        'titulo': (r.get('titulo') or '').strip(),
                        'url': url,
                    })
        return recursos or [{'titulo': '', 'url': ''}]

    def clean(self):
        cleaned = super().clean()
        titulos = self.data.getlist('recurso_titulo') if hasattr(self.data, 'getlist') else []
        urls = self.data.getlist('recurso_url') if hasattr(self.data, 'getlist') else []
        recursos = []
        errores = []
        for i, raw_url in enumerate(urls):
            url = (raw_url or '').strip()
            titulo = (titulos[i] if i < len(titulos) else '').strip()
            if not url and not titulo:
                continue
            if not url.startswith(('http://', 'https://')):
                errores.append(f'Recurso {len(recursos) + 1}: la URL debe empezar con http:// o https://.')
                continue
            recursos.append({'titulo': titulo or f'Recurso {len(recursos) + 1}', 'url': url})
        if errores:
            raise forms.ValidationError(errores)
        cleaned['recursos_lista'] = recursos
        return cleaned

    def clean_nota_minima(self):
        nota = self.cleaned_data.get('nota_minima')
        if nota is None:
            return 11
        if nota < 0 or nota > 20:
            raise forms.ValidationError('La nota mínima debe estar entre 0 y 20.')
        return nota

    def save(self, commit=True, user=None):
        curso = super().save(commit=False)
        curso.tipo = self.tipo_fijo
        curso.recursos = self.cleaned_data.get('recursos_lista') or []
        if self.tipo_fijo == 'INDUCCION':
            curso.alcance = 'TODOS'
        if user and not curso.pk:
            curso.creado_por = user
        if commit:
            curso.save()
            if curso.tipo == 'CAPACITACION' and curso.alcance == 'POR_CARGO':
                curso.cargos_visibles.set(self.cleaned_data.get('cargos') or [])
            else:
                curso.cargos_visibles.clear()
        return curso


class RutaInduccionForm(forms.ModelForm):
    class Meta:
        model = RutaInduccion
        fields = ['cargo', 'activo']
        widgets = {
            'cargo': forms.Select(attrs={'class': 'custom-select form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Cargo.objects.filter(activo=True).select_related('area').order_by('area__nombre', 'nombre')
        if self.instance and self.instance.pk:
            qs = qs.filter(Q(ruta_induccion__isnull=True) | Q(pk=self.instance.cargo_id))
        else:
            qs = qs.filter(ruta_induccion__isnull=True)
        self.fields['cargo'].queryset = qs
        self.fields['cargo'].label_from_instance = (
            lambda c: f'{c.area.nombre} — {c.nombre}' if c.area_id else c.nombre
        )


class RutaInduccionCursoForm(forms.ModelForm):
    class Meta:
        model = RutaInduccionCurso
        fields = ['curso', 'orden', 'prerequisito']
        widgets = {
            'curso': forms.Select(attrs={'class': 'custom-select form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'prerequisito': forms.Select(attrs={'class': 'custom-select form-control'}),
        }

    def __init__(self, *args, ruta=None, **kwargs):
        self.ruta = ruta
        super().__init__(*args, **kwargs)
        cursos_ok = CursoAprendizaje.objects.filter(
            activo=True,
            tipo='INDUCCION',
        ).order_by('nombre')
        if ruta:
            ya = list(ruta.items.values_list('curso_id', flat=True))
            if self.instance and self.instance.curso_id:
                ya = [i for i in ya if i != self.instance.curso_id]
            cursos_ok = cursos_ok.exclude(id__in=ya)
            en_ruta = CursoAprendizaje.objects.filter(
                id__in=ruta.items.values_list('curso_id', flat=True)
            ).order_by('nombre')
            if self.instance and self.instance.curso_id:
                en_ruta = en_ruta.exclude(pk=self.instance.curso_id)
            self.fields['prerequisito'].queryset = en_ruta
        else:
            self.fields['prerequisito'].queryset = CursoAprendizaje.objects.none()
        self.fields['curso'].queryset = cursos_ok
        self.fields['prerequisito'].required = False
        self.fields['prerequisito'].empty_label = '— Sin requisito —'


class CalificarAsignacionForm(forms.Form):
    nota = forms.DecimalField(
        min_value=0,
        max_value=20,
        decimal_places=2,
        label='Nota (0–20)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '20'}),
    )
    comentario_evaluador = forms.CharField(
        required=False,
        label='Comentario',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
