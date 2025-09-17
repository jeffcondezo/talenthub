from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Postulacion, Convocatoria, FormacionAcademica, CursoEspecializacion, ExperienciaLaboral, Persona, CV

class CustomLoginForm(AuthenticationForm):
    """Formulario personalizado de login"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autocomplete': 'username',
            'required': True,
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
            'required': True,
        }),
        label='Contraseña'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
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
            'cv'
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
        }


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
            'certificado': forms.FileInput(attrs={'class': 'form-control'}),
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
            'certificado': 'Certificado',
            'observaciones': 'Observaciones',
        }


class ExperienciaLaboralForm(forms.ModelForm):
    """Formulario para experiencia laboral"""
    
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'tipo_experiencia', 'tipo_entidad', 'nombre_entidad', 'cargo',
            'fecha_inicio', 'fecha_fin', 'salario', 'motivo_salida', 'logros',
            'responsabilidades', 'supervisor', 'telefono_referencia', 'observaciones',
            'cv'
        ]
        widgets = {
            'tipo_experiencia': forms.Select(attrs={'class': 'form-control'}),
            'tipo_entidad': forms.Select(attrs={'class': 'form-control'}),
            'nombre_entidad': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'motivo_salida': forms.TextInput(attrs={'class': 'form-control'}),
            'logros': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsabilidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supervisor': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
        }
