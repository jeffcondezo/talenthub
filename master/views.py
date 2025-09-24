from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .forms import CustomLoginForm, FormacionAcademicaForm, CursoEspecializacionForm, ExperienciaLaboralForm, PostulacionForm, ColaboradorForm
from .models import Persona, Cargo, Area, Convocatoria, Postulacion, FormacionAcademica, CursoEspecializacion, ExperienciaLaboral, CV, Colaborador, Departamento, Provincia, Distrito

# Create your views here.

def induccion_view(request):
    """View para la página de inducción"""
    return render(request, 'master/induccion.html')

def proyecto_view(request):
    """View para la página de proyectos"""
    return render(request, 'master/proyecto.html')

def perfiles_view(request):
    """View para la página de perfiles"""
    return render(request, 'master/perfiles.html')

def capacitacion_view(request):
    """View para la página de capacitación"""
    return render(request, 'master/capacitacion.html')

class CVDetailView(DetailView):
    """
    Vista basada en clases para mostrar el CV completo de una persona
    """
    template_name = 'master/cv.html'
    context_object_name = 'persona'
    model = Persona
    
    def get_object(self):
        """
        Obtiene la persona basada en el ID de la URL
        """
        id = self.kwargs.get('id')
        return Persona.objects.get(id=id)
    
    def get_context_data(self, **kwargs):
        """
        Agrega los datos del CV al contexto
        """
        context = super().get_context_data(**kwargs)
        persona = self.object
        
        # Obtener CV si existe
        try:
            cv = persona.cv
            context['cv'] = cv
            
            # Obtener datos del CV
            context['formaciones_academicas'] = cv.formaciones_academicas.all().order_by('-fecha_expedicion')
            context['cursos_especializacion'] = cv.cursos_especializacion.all().order_by('-fecha_fin')
            context['experiencias_laborales'] = cv.experiencias_laborales.all().order_by('-fecha_inicio')
            
        except CV.DoesNotExist:
            context['cv'] = None
            context['formaciones_academicas'] = []
            context['cursos_especializacion'] = []
            context['experiencias_laborales'] = []
        
        # Información adicional de la persona (sin depender de tipo)
        context['tiene_postulaciones'] = persona.postulaciones.exists()
        context['es_colaborador'] = hasattr(persona, 'colaborador') and persona.colaborador is not None
        
        # Datos adicionales para el contexto
        context['total_formaciones'] = len(context['formaciones_academicas'])
        context['total_cursos'] = len(context['cursos_especializacion'])
        context['total_experiencias'] = len(context['experiencias_laborales'])
        
        return context


def cv_view(request):
    """
    Vista de redirección para mantener compatibilidad
    Redirige a la lista de aspirantes para seleccionar un CV
    """
    return redirect('master:aspirantes')

class AspirantesListView(ListView):
    """
    Vista basada en clases para listar postulaciones con funcionalidades avanzadas
    """
    model = Postulacion
    template_name = 'master/aspirantes.html'
    context_object_name = 'postulaciones'
    paginate_by = 10
    ordering = ['-fecha_postulacion']


class PersonasListView(ListView):
    """
    Vista basada en clases para listar personas
    """
    model = Persona
    template_name = 'master/personas.html'
    context_object_name = 'personas'
    paginate_by = 10
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """
        Filtra las personas según los parámetros de búsqueda
        """
        queryset = Persona.objects.all().order_by('-fecha_creacion')
        
        # Filtro por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) |
                Q(apellido_paterno__icontains=search) |
                Q(apellido_materno__icontains=search) |
                Q(numero_documento__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agrega datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        context['total_personas'] = Persona.objects.count()
        context['personas_con_cv'] = Persona.objects.filter(cv__isnull=False).count()
        context['personas_con_postulaciones'] = Persona.objects.filter(postulaciones__isnull=False).distinct().count()
        context['personas_colaboradores'] = Persona.objects.filter(colaborador__isnull=False).count()
        
        # Parámetros de búsqueda para mantener en la paginación
        context['search'] = self.request.GET.get('search', '')
        
        return context


class PostulantesListView(ListView):
    """
    Vista basada en clases para listar postulantes de una convocatoria específica
    """
    model = Postulacion
    template_name = 'master/postulantes.html'
    context_object_name = 'postulaciones'
    paginate_by = 10
    ordering = ['-fecha_postulacion']
    
    def get_queryset(self):
        """
        Filtra las postulaciones por convocatoria y parámetros de búsqueda
        """
        convocatoria_id = self.kwargs.get('convocatoria_id')
        queryset = Postulacion.objects.filter(convocatoria_id=convocatoria_id).select_related(
            'persona', 'convocatoria', 'convocatoria__cargo'
        ).order_by('-fecha_postulacion')
        
        # Filtro por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(persona__nombres__icontains=search) |
                Q(persona__apellido_paterno__icontains=search) |
                Q(persona__apellido_materno__icontains=search) |
                Q(persona__numero_documento__icontains=search) |
                Q(persona__email__icontains=search)
            )
        
        # Filtro por estado de postulación
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado_postulacion=estado)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agrega datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        convocatoria_id = self.kwargs.get('convocatoria_id')
        
        # Obtener la convocatoria
        try:
            convocatoria = Convocatoria.objects.select_related('cargo', 'cargo__area').get(id=convocatoria_id)
            context['convocatoria'] = convocatoria
        except Convocatoria.DoesNotExist:
            context['convocatoria'] = None
        
        # Estadísticas de postulaciones para esta convocatoria
        postulaciones_queryset = Postulacion.objects.filter(convocatoria_id=convocatoria_id)
        context['total_postulaciones'] = postulaciones_queryset.count()
        context['postulaciones_por_estado'] = {
            'POSTULADO': postulaciones_queryset.filter(estado_postulacion='POSTULADO').count(),
            'EN_REVISION': postulaciones_queryset.filter(estado_postulacion='EN_REVISION').count(),
            'ENTREVISTA': postulaciones_queryset.filter(estado_postulacion='ENTREVISTA').count(),
            'EVALUACION': postulaciones_queryset.filter(estado_postulacion='EVALUACION').count(),
            'APROBADO': postulaciones_queryset.filter(estado_postulacion='APROBADO').count(),
            'RECHAZADO': postulaciones_queryset.filter(estado_postulacion='RECHAZADO').count(),
            'RETIRADO': postulaciones_queryset.filter(estado_postulacion='RETIRADO').count(),
        }
        
        # Parámetros de búsqueda para mantener en la paginación
        context['search'] = self.request.GET.get('search', '')
        context['estado'] = self.request.GET.get('estado', '')
        
        # Opciones de estado para el filtro
        context['estado_choices'] = Postulacion.ESTADO_POSTULACION_CHOICES
        
        return context


class PersonaCreateView(CreateView):
    """
    Vista basada en clases para crear una nueva persona
    """
    model = Persona
    template_name = 'master/persona_create.html'
    fields = [
        'tipo_documento', 'numero_documento', 'apellido_paterno', 'apellido_materno', 
        'nombres', 'fecha_nacimiento', 'sexo', 'estado_civil', 'celular', 'email',
        'direccion', 'distrito', 'provincia', 'departamento'
    ]
    success_url = reverse_lazy('master:personas')

    def get(self, request, *args, **kwargs):
        """Mostrar formulario de creación"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            # Para CreateView, no hay objeto aún, solo el formulario
            form = self.get_form()
            context = {'form': form}
            html = render_to_string(self.template_name, context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Procesar formulario válido
        """
        # Guardar el objeto
        self.object = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Persona creada correctamente'})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Procesar formulario inválido
        """
        # Si es petición AJAX, devolver errores en JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_invalid(form)


class PersonaDetailView(DetailView):
    """
    Vista basada en clases para mostrar el detalle completo de una persona
    """
    model = Persona
    template_name = 'master/persona_detail.html'
    context_object_name = 'persona'
    pk_url_kwarg = 'id'
    
    def get(self, request, *args, **kwargs):
        """Mostrar detalles de la persona"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            # Establecer el objeto primero
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string(self.template_name, context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        persona = self.get_object()
        
        # Obtener CV si existe
        try:
            context['cv'] = persona.cv
        except CV.DoesNotExist:
            context['cv'] = None
        
        # Obtener postulaciones
        context['postulaciones'] = persona.postulaciones.all().order_by('-fecha_postulacion')
        
        # Obtener información de colaborador si existe
        try:
            context['colaborador'] = persona.colaborador
        except Colaborador.DoesNotExist:
            context['colaborador'] = None
        
        # Obtener la postulación específica si se proporciona el ID
        postulacion_id = self.request.GET.get('postulacion_id')
        if postulacion_id:
            try:
                context['postulacion_actual'] = persona.postulaciones.get(id=postulacion_id)
            except Postulacion.DoesNotExist:
                context['postulacion_actual'] = None
        else:
            context['postulacion_actual'] = None
        
        return context


class PersonaUpdateView(UpdateView):
    """
    Vista basada en clases para editar una persona
    """
    model = Persona
    template_name = 'master/persona_edit.html'
    context_object_name = 'persona'
    pk_url_kwarg = 'id'
    fields = [
        'tipo_documento', 'numero_documento', 'apellido_paterno', 'apellido_materno', 
        'nombres', 'fecha_nacimiento', 'sexo', 'estado_civil', 'celular', 'email',
        'direccion', 'distrito', 'provincia', 'departamento'
    ]
    success_url = reverse_lazy('master:personas')
    
    def get(self, request, *args, **kwargs):
        """Mostrar formulario de edición"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            # Establecer el objeto primero
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string(self.template_name, context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Procesar formulario válido
        """
        # Guardar el objeto
        self.object = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Persona actualizada correctamente'})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Procesar formulario inválido
        """
        # Si es petición AJAX, devolver errores en JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_invalid(form)


class PersonaDeleteView(DeleteView):
    """
    Vista basada en clases para eliminar una persona
    """
    model = Persona
    template_name = 'master/persona_confirm_delete.html'
    context_object_name = 'persona'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('master:personas')
    
    def get(self, request, *args, **kwargs):
        """Mostrar confirmación de eliminación"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            # Establecer el objeto primero
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string(self.template_name, context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        persona = self.get_object()
        
        # Verificar si tiene postulaciones
        context['tiene_postulaciones'] = persona.postulaciones.exists()
        context['tiene_cv'] = hasattr(persona, 'cv')
        context['es_colaborador'] = hasattr(persona, 'colaborador')
        
        return context
    
    def delete(self, request, *args, **kwargs):
        """Manejar eliminación con soporte para AJAX"""
        persona = self.get_object()
        persona_nombre = persona.nombre_completo
        
        # Eliminar el objeto
        persona.delete()
        
        # Si es petición AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Persona eliminada correctamente'})
        
        # Redirigir a la lista de personas
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.success_url)


class ConvocatoriasListView(ListView):
    """
    Vista basada en clases para listar convocatorias con funcionalidades avanzadas
    """
    model = Convocatoria
    template_name = 'master/convocatorias.html'
    context_object_name = 'convocatorias'
    paginate_by = 10
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """
        Obtener queryset con filtros opcionales
        """
        # Crear queryset base desde cero para evitar problemas de caché
        queryset = Convocatoria.objects.select_related(
            'cargo__area'
        ).order_by('-fecha_creacion')
        
        # Filtro por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(cargo__nombre__icontains=search) |
                Q(cargo__area__nombre__icontains=search) |
                Q(responsable_rrhh__icontains=search) |
                Q(ubicacion__icontains=search)
            )
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por cargo
        cargo = self.request.GET.get('cargo')
        if cargo:
            queryset = queryset.filter(cargo_id=cargo)
        
        # Filtro por área
        area = self.request.GET.get('area')
        if area:
            queryset = queryset.filter(cargo__area_id=area)
        
        # Filtro por activo
        activo = self.request.GET.get('activo')
        if activo:
            queryset = queryset.filter(activo=activo == 'true')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        
        # Agregar opciones para filtros - usando consultas explícitas
        try:
            context['cargos'] = Cargo.objects.filter(activo=True).select_related('area')
            context['areas'] = Area.objects.filter(activo=True)
            context['estados_choices'] = Convocatoria.ESTADO_CONVOCATORIA_CHOICES
            context['tipos_choices'] = Convocatoria.TIPO_CONVOCATORIA_CHOICES
        except Exception:
            # En caso de error, usar listas vacías
            context['cargos'] = []
            context['areas'] = []
            context['estados_choices'] = []
            context['tipos_choices'] = []
        
        # Mantener filtros en la URL
        context['current_search'] = self.request.GET.get('search', '')
        context['current_estado'] = self.request.GET.get('estado', '')
        context['current_tipo'] = self.request.GET.get('tipo', '')
        context['current_cargo'] = self.request.GET.get('cargo', '')
        context['current_area'] = self.request.GET.get('area', '')
        context['current_activo'] = self.request.GET.get('activo', '')
        
        # Estadísticas básicas - usando consultas explícitas
        try:
            context['total_convocatorias'] = Convocatoria.objects.count()
            context['convocatorias_activas'] = Convocatoria.objects.filter(activo=True).count()
            context['convocatorias_publicadas'] = Convocatoria.objects.filter(estado='PUBLICADA').count()
            context['convocatorias_abiertas'] = Convocatoria.objects.filter(
                estado='PUBLICADA',
                fecha_apertura__lte=timezone.now(),
                fecha_cierre__gte=timezone.now()
            ).count()
        except Exception:
            # En caso de error, usar valores por defecto
            context['total_convocatorias'] = 0
            context['convocatorias_activas'] = 0
            context['convocatorias_publicadas'] = 0
            context['convocatorias_abiertas'] = 0
        
        return context

def colaboradores_view(request):
    """View para la página de colaboradores"""
    return render(request, 'master/colaboradores.html')

class CustomLoginView(LoginView):
    """Vista basada en clases para el login"""
    
    template_name = 'master/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirigir a inducción después del login exitoso"""
        return reverse_lazy('master:induccion')
    
    def form_valid(self, form):
        """Procesar login exitoso""" 
        # Llamar al método padre para manejar el login automáticamente
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Procesar login fallido"""
        # El formulario ya maneja los mensajes de error personalizados
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Agregar datos adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar Sesión'
        return context

class CustomLogoutView(LogoutView):
    """Vista basada en clases para el logout"""
    
    next_page = reverse_lazy('master:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Procesar logout con mensaje personalizado"""
        # Obtener el nombre de usuario antes del logout
        username = request.user.username if request.user.is_authenticated else 'Usuario'
        
        # Hacer logout
        response = super().dispatch(request, *args, **kwargs)
        
        # Agregar mensaje de despedida
        messages.success(request, f'¡Hasta luego, {username}! Has cerrado sesión correctamente.')
        
        return response


class ConvocatoriaDetailView(DetailView):
    """
    Vista basada en clases para mostrar el detalle completo de una convocatoria
    """
    model = Convocatoria
    template_name = 'master/convocatoria_detail.html'
    context_object_name = 'convocatoria'
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        convocatoria = self.get_object()
        
        # Agregar estadísticas de postulaciones
        try:
            context['total_postulaciones'] = convocatoria.postulaciones.count()
            context['postulaciones_por_estado'] = {}
            for estado, label in Postulacion.ESTADO_POSTULACION_CHOICES:
                count = convocatoria.postulaciones.filter(estado_postulacion=estado).count()
                context['postulaciones_por_estado'][estado] = {
                    'label': label,
                    'count': count
                }
        except Exception:
            context['total_postulaciones'] = 0
            context['postulaciones_por_estado'] = {}
        
        return context


class ConvocatoriaCreateView(CreateView):
    """
    Vista basada en clases para crear una nueva convocatoria
    """
    model = Convocatoria
    template_name = 'master/convocatoria_create.html'
    fields = [
        'titulo', 'descripcion', 'cargo', 'fecha_apertura', 'fecha_cierre',
        'fecha_inicio_trabajo', 'estado', 'tipo', 'nombre_empresa_externa', 'requisitos_minimos',
        'requisitos_deseables', 'experiencia_minima', 'numero_vacantes',
        'salario_ofrecido', 'modalidad_trabajo', 'ubicacion', 'responsable_rrhh', 'activo'
    ]
    success_url = reverse_lazy('master:convocatorias')
    
    def get(self, request, *args, **kwargs):
        """Mostrar formulario de creación"""
        # Si es petición AJAX, devolver solo el contenido del formulario
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            # Establecer el objeto primero
            self.object = None
            context = self.get_context_data()
            # Renderizar el template completo y extraer solo el formulario
            html = render_to_string('master/convocatoria_create.html', context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Procesar formulario válido
        """
        # Guardar el objeto
        self.object = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Convocatoria creada correctamente'})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Procesar formulario inválido
        """
        # Si es petición AJAX, devolver errores en JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

class ConvocatoriaUpdateView(UpdateView):
    """
    Vista basada en clases para editar una convocatoria
    """
    model = Convocatoria
    template_name = 'master/convocatoria_edit.html'
    context_object_name = 'convocatoria'
    pk_url_kwarg = 'id'
    fields = [
        'titulo', 'descripcion', 'cargo', 'fecha_apertura', 'fecha_cierre',
        'fecha_inicio_trabajo', 'estado', 'tipo', 'nombre_empresa_externa', 'requisitos_minimos',
        'requisitos_deseables', 'experiencia_minima', 'numero_vacantes',
        'salario_ofrecido', 'modalidad_trabajo', 'ubicacion', 'responsable_rrhh', 'activo'
    ]
    success_url = reverse_lazy('master:convocatorias')
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        
        # Agregar opciones para los campos de selección
        try:
            context['cargos'] = Cargo.objects.filter(activo=True).select_related('area')
            context['areas'] = Area.objects.filter(activo=True)
            context['estados_choices'] = Convocatoria.ESTADO_CONVOCATORIA_CHOICES
            context['tipos_choices'] = Convocatoria.TIPO_CONVOCATORIA_CHOICES
        except Exception:
            context['cargos'] = []
            context['areas'] = []
            context['estados_choices'] = []
            context['tipos_choices'] = []
        
        return context
    
    def form_valid(self, form):
        """
        Procesar formulario válido
        """
        response = super().form_valid(form)
        messages.success(self.request, f'Convocatoria "{self.object.titulo}" actualizada correctamente.')
        return response
    
    def form_invalid(self, form):
        """
        Procesar formulario inválido
        """
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class ConvocatoriaDeleteView(DeleteView):
    """
    Vista basada en clases para eliminar una convocatoria
    """
    model = Convocatoria
    template_name = 'master/convocatoria_confirm_delete.html'
    context_object_name = 'convocatoria'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('master:convocatorias')
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        convocatoria = self.get_object()
        
        # Contar registros relacionados que se eliminarán
        try:
            context['total_postulaciones'] = convocatoria.postulaciones.count()
            context['postulaciones_por_estado'] = {}
            for estado, label in Postulacion.ESTADO_POSTULACION_CHOICES:
                count = convocatoria.postulaciones.filter(estado_postulacion=estado).count()
                if count > 0:
                    context['postulaciones_por_estado'][estado] = {
                        'label': label,
                        'count': count
                    }
        except Exception:
            context['total_postulaciones'] = 0
            context['postulaciones_por_estado'] = {}
        
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Procesar eliminación
        """
        convocatoria = self.get_object()
        titulo = convocatoria.titulo
        total_postulaciones = convocatoria.postulaciones.count()
        
        # Eliminar la convocatoria
        convocatoria.delete()
        
        # Mensaje de confirmación
        if total_postulaciones > 0:
            messages.success(
                request, 
                f'Convocatoria "{titulo}" eliminada correctamente. '
                f'Se eliminaron {total_postulaciones} postulaciones relacionadas.'
            )
        else:
            messages.success(request, f'Convocatoria "{titulo}" eliminada correctamente.')
        
        # Redirigir a la lista de convocatorias
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.success_url)


# ===== VISTAS PARA GESTIÓN DE CV =====

class FormacionAcademicaCreateView(CreateView):
    """Vista para crear formación académica"""
    model = FormacionAcademica
    form_class = FormacionAcademicaForm
    template_name = 'master/cv_formacion_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['es_edicion'] = False
        
        # Obtener o crear CV para la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        
        # Inicializar el CV en el formulario
        context['form'].fields['cv'].initial = cv.id
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_formacion_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        # Obtener o crear CV para la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        
        # Asignar el CV al formulario
        form.instance.cv = cv
        formacion = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Formación académica creada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=self.kwargs['persona_id'])
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        # Si es petición AJAX, devolver errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return super().form_invalid(form)


class FormacionAcademicaUpdateView(UpdateView):
    """Vista para editar formación académica"""
    model = FormacionAcademica
    form_class = FormacionAcademicaForm
    template_name = 'master/cv_formacion_form.html'
    pk_url_kwarg = 'formacion_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['es_edicion'] = True
        
        # Obtener CV de la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        try:
            cv = persona.cv
            context['form'].fields['cv'].initial = cv.id
        except CV.DoesNotExist:
            # Si no existe CV, crear uno
            cv, created = CV.objects.get_or_create(persona=persona)
            context['form'].fields['cv'].initial = cv.id
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_formacion_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        # Asegurar que el CV esté asignado correctamente
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        form.instance.cv = cv
        
        formacion = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Formación académica actualizada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=self.kwargs['persona_id'])
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        # Si es petición AJAX, devolver errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return super().form_invalid(form)


class FormacionAcademicaDeleteView(DeleteView):
    """Vista para eliminar formación académica"""
    model = FormacionAcademica
    pk_url_kwarg = 'formacion_id'
    template_name = 'master/formacionacademica_confirm_delete.html'
    
    def get(self, request, *args, **kwargs):
        """Mostrar confirmación de eliminación"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            context = {'object': self.get_object()}
            html = render_to_string(self.template_name, context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Manejar eliminación con soporte para AJAX"""
        formacion = self.get_object()
        
        # Obtener información antes de eliminar
        persona_id = formacion.cv.persona.id
        
        # Eliminar el objeto
        formacion.delete()
        
        # Si es petición AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Formación académica eliminada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=persona_id)
    
    def get_success_url(self):
        """Redirige al CV después de eliminar"""
        formacion = self.get_object()
        return reverse('master:cv_detail', kwargs={'id': formacion.cv.persona.id})


class CursoEspecializacionCreateView(CreateView):
    """Vista para crear curso de especialización"""
    model = CursoEspecializacion
    form_class = CursoEspecializacionForm
    template_name = 'master/cv_curso_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['es_edicion'] = False
        
        # Obtener o crear CV para la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        
        # Inicializar el CV en el formulario
        context['form'].fields['cv'].initial = cv.id
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_curso_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        # Obtener o crear CV para la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        
        # Asignar el CV al formulario
        form.instance.cv = cv
        curso = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Curso de especialización creado correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=self.kwargs['persona_id'])
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        # Si es petición AJAX, devolver errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return super().form_invalid(form)


class CursoEspecializacionUpdateView(UpdateView):
    """Vista para editar curso de especialización"""
    model = CursoEspecializacion
    form_class = CursoEspecializacionForm
    template_name = 'master/cv_curso_form.html'
    pk_url_kwarg = 'curso_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['es_edicion'] = True
        
        # Obtener CV de la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        try:
            cv = persona.cv
            context['form'].fields['cv'].initial = cv.id
        except CV.DoesNotExist:
            # Si no existe CV, crear uno
            cv, created = CV.objects.get_or_create(persona=persona)
            context['form'].fields['cv'].initial = cv.id
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_curso_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        # Asegurar que el CV esté asignado correctamente
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        form.instance.cv = cv
        
        curso = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Curso de especialización actualizado correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=self.kwargs['persona_id'])
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        # Si es petición AJAX, devolver errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return super().form_invalid(form)


class CursoEspecializacionDeleteView(DeleteView):
    """Vista para eliminar curso de especialización"""
    model = CursoEspecializacion
    pk_url_kwarg = 'curso_id'
    template_name = 'master/cursoespecializacion_confirm_delete.html'
    
    def get(self, request, *args, **kwargs):
        """Mostrar confirmación de eliminación"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            context = {'object': self.get_object()}
            html = render_to_string(self.template_name, context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Manejar eliminación con soporte para AJAX"""
        curso = self.get_object()
        
        # Obtener información antes de eliminar
        persona_id = curso.cv.persona.id
        
        # Eliminar el objeto
        curso.delete()
        
        # Si es petición AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Curso de especialización eliminado correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=persona_id)
    
    def get_success_url(self):
        """Redirige al CV después de eliminar"""
        curso = self.get_object()
        return reverse('master:cv_detail', kwargs={'id': curso.cv.persona.id})


class ExperienciaLaboralCreateView(CreateView):
    """Vista para crear experiencia laboral"""
    model = ExperienciaLaboral
    form_class = ExperienciaLaboralForm
    template_name = 'master/cv_experiencia_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['es_edicion'] = False
        
        # Obtener o crear CV para la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        
        # Inicializar el CV en el formulario
        context['form'].fields['cv'].initial = cv.id
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_experiencia_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        # Obtener o crear CV para la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        
        # Asignar el CV al formulario
        form.instance.cv = cv
        experiencia = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Experiencia laboral creada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=self.kwargs['persona_id'])
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        # Si es petición AJAX, devolver errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return super().form_invalid(form)


class ExperienciaLaboralUpdateView(UpdateView):
    """Vista para editar experiencia laboral"""
    model = ExperienciaLaboral
    form_class = ExperienciaLaboralForm
    template_name = 'master/cv_experiencia_form.html'
    pk_url_kwarg = 'experiencia_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['es_edicion'] = True
        
        # Obtener CV de la persona
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        try:
            cv = persona.cv
            context['form'].fields['cv'].initial = cv.id
        except CV.DoesNotExist:
            # Si no existe CV, crear uno
            cv, created = CV.objects.get_or_create(persona=persona)
            context['form'].fields['cv'].initial = cv.id
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_experiencia_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        # Asegurar que el CV esté asignado correctamente
        persona = get_object_or_404(Persona, id=self.kwargs['persona_id'])
        cv, created = CV.objects.get_or_create(persona=persona)
        form.instance.cv = cv
        
        experiencia = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Experiencia laboral actualizada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=self.kwargs['persona_id'])
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        # Si es petición AJAX, devolver errores
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return super().form_invalid(form)


class ExperienciaLaboralDeleteView(DeleteView):
    """Vista para eliminar experiencia laboral"""
    model = ExperienciaLaboral
    pk_url_kwarg = 'experiencia_id'
    template_name = 'master/experiencialaboral_confirm_delete.html'
    
    def get(self, request, *args, **kwargs):
        """Mostrar confirmación de eliminación"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            context = {'object': self.get_object()}
            html = render_to_string(self.template_name, context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Manejar eliminación con soporte para AJAX"""
        experiencia = self.get_object()
        
        # Obtener información antes de eliminar
        persona_id = experiencia.cv.persona.id
        
        # Eliminar el objeto
        experiencia.delete()
        
        # Si es petición AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Experiencia laboral eliminada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', id=persona_id)
    
    def get_success_url(self):
        """Redirige al CV después de eliminar"""
        experiencia = self.get_object()
        return reverse('master:cv_detail', kwargs={'id': experiencia.cv.persona.id})


# Vistas AJAX para filtrado en cascada de ubicaciones
def get_provincias(request):
    """Obtener provincias por departamento"""
    departamento_id = request.GET.get('departamento_id')
    if departamento_id:
        provincias = Provincia.objects.filter(departamento_id=departamento_id).order_by('nombre')
        data = [{'id': p.id, 'nombre': p.nombre} for p in provincias]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_distritos(request):
    """Obtener distritos por provincia"""
    provincia_id = request.GET.get('provincia_id')
    if provincia_id:
        distritos = Distrito.objects.filter(provincia_id=provincia_id).order_by('nombre')
        data = [{'id': d.id, 'nombre': d.nombre} for d in distritos]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def crear_postulacion(request, persona_id):
    """
    Vista para crear una nueva postulación para una persona
    """
    if request.method == 'POST':
        try:
            persona = get_object_or_404(Persona, id=persona_id)
            convocatoria_id = request.POST.get('convocatoria_id')
            estado_postulacion = request.POST.get('estado_postulacion', 'POSTULADO')
            observaciones = request.POST.get('observaciones', '')
            
            if not convocatoria_id:
                return JsonResponse({'success': False, 'errors': {'convocatoria_id': ['Este campo es obligatorio']}})
            
            convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)
            
            # Crear la postulación
            postulacion = Postulacion.objects.create(
                persona=persona,
                convocatoria=convocatoria,
                estado_postulacion=estado_postulacion,
                observaciones=observaciones
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Postulación creada correctamente'})
            
            messages.success(request, 'Postulación creada correctamente')
            return redirect('master:persona_detail', id=persona_id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
            
            messages.error(request, f'Error al crear postulación: {str(e)}')
            return redirect('master:persona_detail', id=persona_id)
    
    return JsonResponse({'success': False, 'errors': {'method': ['Método no permitido']}})


def get_convocatorias(request):
    """Obtener convocatorias activas para el formulario de postulación"""
    convocatorias = Convocatoria.objects.filter(
        estado='PUBLICADA',
        fecha_cierre__gte=timezone.now()
    ).order_by('titulo')
    
    data = [{'id': c.id, 'titulo': c.titulo} for c in convocatorias]
    return JsonResponse(data, safe=False)


class PostulacionUpdateView(UpdateView):
    """Vista para editar una postulación"""
    model = Postulacion
    form_class = PostulacionForm
    template_name = 'master/postulacion_edit.html'
    context_object_name = 'postulacion'
    
    def get(self, request, *args, **kwargs):
        """Mostrar formulario de edición"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            # Establecer el objeto primero
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string('master/postulacion_edit_modal.html', context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, usar el comportamiento por defecto
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Procesar formulario válido
        """
        # Guardar el objeto
        self.object = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Postulación actualizada correctamente'})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Procesar formulario inválido
        """
        # Si es petición AJAX, devolver errores en JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': form.errors})

        # Para peticiones normales, usar el comportamiento por defecto
        return super().form_invalid(form)
    
    def get_success_url(self):
        """Redirigir a la lista de postulantes de la convocatoria"""
        return reverse('master:postulantes', kwargs={'convocatoria_id': self.object.convocatoria.id})
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional"""
        context = super().get_context_data(**kwargs)
        context['convocatoria'] = self.object.convocatoria
        context['persona'] = self.object.persona
        return context


def registro_postulante(request):
    """
    Vista para que los postulantes se registren públicamente (solo datos básicos)
    """
    if request.method == 'POST':
        try:
            from datetime import datetime
            
            # Obtener las instancias de los modelos de ubicación
            departamento = Departamento.objects.get(id=request.POST.get('departamento'))
            provincia = Provincia.objects.get(id=request.POST.get('provincia'))
            distrito = Distrito.objects.get(id=request.POST.get('distrito'))
            
            # Convertir fecha de nacimiento de string a date
            fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date() if fecha_nacimiento_str else None
            
            # Crear persona
            persona_data = {
                'tipo_documento': request.POST.get('tipo_documento'),
                'numero_documento': request.POST.get('numero_documento'),
                'nombres': request.POST.get('nombres'),
                'apellido_paterno': request.POST.get('apellido_paterno'),
                'apellido_materno': request.POST.get('apellido_materno'),
                'fecha_nacimiento': fecha_nacimiento,
                'sexo': request.POST.get('sexo'),
                'celular': request.POST.get('telefono'),
                'email': request.POST.get('email'),
                'direccion': request.POST.get('direccion'),
                'departamento': departamento,
                'provincia': provincia,
                'distrito': distrito,
            }
            
            # Crear la persona
            persona = Persona.objects.create(**persona_data)
            
            # Crear CV básico
            cv_data = {
                'persona': persona,
                'resumen_profesional': '',
                'objetivo_profesional': '',
            }
            
            cv = CV.objects.create(**cv_data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True, 
                    'message': 'Registro completado exitosamente.',
                    'redirect_url': f'/master/postulante/{persona.id}/'
                })
            
            from django.contrib import messages
            messages.success(request, 'Registro completado exitosamente.')
            return redirect('master:postulante_detail', persona_id=persona.id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
            
            from django.contrib import messages
            messages.error(request, f'Error al registrar: {str(e)}')
            return redirect('master:registro_postulante')
    
    # Para peticiones GET, mostrar el formulario
    context = {
        'departamentos': Departamento.objects.all(),
        'provincias': Provincia.objects.none(),
        'distritos': Distrito.objects.none(),
    }
    return render(request, 'master/registro_postulante.html', context)

def postulante_detail(request, persona_id):
    """
    Vista de detalle del postulante con opciones para agregar datos del CV
    """
    try:
        persona = Persona.objects.get(id=persona_id)
        cv = CV.objects.get(persona=persona)
        formaciones = FormacionAcademica.objects.filter(cv=cv)
        cursos = CursoEspecializacion.objects.filter(cv=cv)
        experiencias = ExperienciaLaboral.objects.filter(cv=cv)
        
        
        context = {
            'persona': persona,
            'cv': cv,
            'formaciones': formaciones,
            'cursos': cursos,
            'experiencias': experiencias,
        }
        return render(request, 'master/postulante_detail.html', context)
    except Persona.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Postulante no encontrado.')
        return redirect('master:registro_postulante')
    except CV.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'CV no encontrado.')
        return redirect('master:registro_postulante')

def agregar_formacion(request, persona_id):
    """
    Vista para agregar formación académica via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            
            # Convertir fechas de string a date
            from datetime import datetime
            fecha_expedicion = None
            fecha_inicio = None
            fecha_fin = None
            
            if request.POST.get('fecha_expedicion'):
                fecha_expedicion = datetime.strptime(request.POST.get('fecha_expedicion'), '%Y-%m-%d').date()
            if request.POST.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            if request.POST.get('fecha_fin'):
                fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            
            formacion = FormacionAcademica.objects.create(
                cv=cv,
                grado=request.POST.get('grado'),
                especialidad=request.POST.get('especialidad'),
                centro_estudio=request.POST.get('centro_estudio'),
                ciudad=request.POST.get('ciudad'),
                pais=request.POST.get('pais'),
                fecha_expedicion=fecha_expedicion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                promedio=request.POST.get('promedio') or None,
                observaciones=request.POST.get('observaciones') or None,
            )
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': 'Formación académica agregada correctamente.',
                'formacion': {
                    'id': formacion.id,
                    'grado': formacion.get_grado_display(),
                    'especialidad': formacion.especialidad,
                    'centro_estudio': formacion.centro_estudio,
                    'ciudad': formacion.ciudad,
                    'pais': formacion.pais,
                    'fecha_expedicion': formacion.fecha_expedicion.strftime('%Y-%m-%d') if formacion.fecha_expedicion else '',
                    'fecha_inicio': formacion.fecha_inicio.strftime('%Y-%m-%d') if formacion.fecha_inicio else '',
                    'fecha_fin': formacion.fecha_fin.strftime('%Y-%m-%d') if formacion.fecha_fin else '',
                    'promedio': str(formacion.promedio) if formacion.promedio else '',
                    'observaciones': formacion.observaciones or '',
                }
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    return render(request, 'master/modal_formacion.html')

def editar_formacion(request, persona_id, formacion_id):
    """
    Vista para editar formación académica via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            formacion = FormacionAcademica.objects.get(id=formacion_id, cv=cv)
            
            # Convertir fechas de string a date
            from datetime import datetime
            fecha_expedicion = None
            fecha_inicio = None
            fecha_fin = None
            
            if request.POST.get('fecha_expedicion'):
                fecha_expedicion = datetime.strptime(request.POST.get('fecha_expedicion'), '%Y-%m-%d').date()
            if request.POST.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            if request.POST.get('fecha_fin'):
                fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            
            # Actualizar la formación
            formacion.grado = request.POST.get('grado')
            formacion.especialidad = request.POST.get('especialidad')
            formacion.centro_estudio = request.POST.get('centro_estudio')
            formacion.ciudad = request.POST.get('ciudad')
            formacion.pais = request.POST.get('pais')
            formacion.fecha_expedicion = fecha_expedicion
            formacion.fecha_inicio = fecha_inicio
            formacion.fecha_fin = fecha_fin
            formacion.promedio = request.POST.get('promedio') or None
            formacion.observaciones = request.POST.get('observaciones') or None
            formacion.save()
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': 'Formación académica actualizada correctamente.',
                'formacion': {
                    'id': formacion.id,
                    'grado': formacion.get_grado_display(),
                    'especialidad': formacion.especialidad,
                    'centro_estudio': formacion.centro_estudio,
                    'ciudad': formacion.ciudad,
                    'pais': formacion.pais,
                    'fecha_expedicion': formacion.fecha_expedicion.strftime('%Y-%m-%d') if formacion.fecha_expedicion else '',
                    'fecha_inicio': formacion.fecha_inicio.strftime('%Y-%m-%d') if formacion.fecha_inicio else '',
                    'fecha_fin': formacion.fecha_fin.strftime('%Y-%m-%d') if formacion.fecha_fin else '',
                    'promedio': str(formacion.promedio) if formacion.promedio else '',
                    'observaciones': formacion.observaciones or '',
                }
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    # Para peticiones GET, mostrar el formulario con datos existentes
    try:
        persona = Persona.objects.get(id=persona_id)
        cv = CV.objects.get(persona=persona)
        formacion = FormacionAcademica.objects.get(id=formacion_id, cv=cv)
        
        context = {
            'formacion': formacion,
            'es_edicion': True,
        }
        return render(request, 'master/modal_formacion.html', context)
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})

def eliminar_formacion(request, persona_id, formacion_id):
    """
    Vista para eliminar formación académica via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            formacion = FormacionAcademica.objects.get(id=formacion_id, cv=cv)
            especialidad = formacion.especialidad
            formacion.delete()
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': f'Formación académica "{especialidad}" eliminada correctamente.'
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    # Para peticiones GET, mostrar modal de confirmación
    try:
        persona = Persona.objects.get(id=persona_id)
        cv = CV.objects.get(persona=persona)
        formacion = FormacionAcademica.objects.get(id=formacion_id, cv=cv)
        
        context = {
            'formacion': formacion,
        }
        return render(request, 'master/modal_eliminar_formacion.html', context)
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})

def agregar_curso(request, persona_id):
    """
    Vista para agregar curso de especialización via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            
            # Convertir fechas de string a date
            from datetime import datetime
            fecha_inicio = None
            fecha_fin = None
            
            if request.POST.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            if request.POST.get('fecha_fin'):
                fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            
            curso = CursoEspecializacion.objects.create(
                cv=cv,
                tipo_estudio=request.POST.get('tipo_estudio'),
                descripcion=request.POST.get('descripcion'),
                institucion=request.POST.get('institucion'),
                pais=request.POST.get('pais'),
                ciudad=request.POST.get('ciudad'),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                horas_lectivas=request.POST.get('horas_lectivas') or None,
                nivel=request.POST.get('nivel') or None,
                observaciones=request.POST.get('observaciones') or None,
            )
            
            # Manejar archivo de certificado si se proporciona
            if 'certificado' in request.FILES:
                curso.certificado = request.FILES['certificado']
                curso.save()
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': 'Curso de especialización agregado correctamente.',
                'curso': {
                    'id': curso.id,
                    'tipo_estudio': curso.get_tipo_estudio_display(),
                    'descripcion': curso.descripcion,
                    'institucion': curso.institucion,
                    'pais': curso.pais,
                    'ciudad': curso.ciudad,
                    'fecha_inicio': curso.fecha_inicio.strftime('%Y-%m-%d') if curso.fecha_inicio else '',
                    'fecha_fin': curso.fecha_fin.strftime('%Y-%m-%d') if curso.fecha_fin else '',
                    'horas_lectivas': str(curso.horas_lectivas) if curso.horas_lectivas else '',
                    'nivel': curso.get_nivel_display() if curso.nivel else '',
                    'certificado': curso.certificado.url if curso.certificado else '',
                    'certificado_nombre': curso.certificado.name if curso.certificado else '',
                    'observaciones': curso.observaciones or '',
                }
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    return render(request, 'master/modal_curso.html')

def editar_curso(request, persona_id, curso_id):
    """
    Vista para editar curso de especialización via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            curso = CursoEspecializacion.objects.get(id=curso_id, cv=cv)
            
            # Convertir fechas de string a date
            from datetime import datetime
            fecha_inicio = None
            fecha_fin = None
            
            if request.POST.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            if request.POST.get('fecha_fin'):
                fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            
            # Actualizar el curso
            curso.tipo_estudio = request.POST.get('tipo_estudio')
            curso.descripcion = request.POST.get('descripcion')
            curso.institucion = request.POST.get('institucion')
            curso.pais = request.POST.get('pais')
            curso.ciudad = request.POST.get('ciudad')
            curso.fecha_inicio = fecha_inicio
            curso.fecha_fin = fecha_fin
            curso.horas_lectivas = request.POST.get('horas_lectivas') or None
            curso.nivel = request.POST.get('nivel') or None
            curso.observaciones = request.POST.get('observaciones') or None
            
            # Manejar archivo de certificado si se proporciona uno nuevo
            if 'certificado' in request.FILES:
                curso.certificado = request.FILES['certificado']
            
            curso.save()
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': 'Curso de especialización actualizado correctamente.',
                'curso': {
                    'id': curso.id,
                    'tipo_estudio': curso.get_tipo_estudio_display(),
                    'descripcion': curso.descripcion,
                    'institucion': curso.institucion,
                    'pais': curso.pais,
                    'ciudad': curso.ciudad,
                    'fecha_inicio': curso.fecha_inicio.strftime('%Y-%m-%d') if curso.fecha_inicio else '',
                    'fecha_fin': curso.fecha_fin.strftime('%Y-%m-%d') if curso.fecha_fin else '',
                    'horas_lectivas': str(curso.horas_lectivas) if curso.horas_lectivas else '',
                    'nivel': curso.get_nivel_display() if curso.nivel else '',
                    'certificado': curso.certificado.url if curso.certificado else '',
                    'certificado_nombre': curso.certificado.name if curso.certificado else '',
                    'observaciones': curso.observaciones or '',
                }
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    # Para peticiones GET, mostrar el formulario con datos existentes
    try:
        persona = Persona.objects.get(id=persona_id)
        cv = CV.objects.get(persona=persona)
        curso = CursoEspecializacion.objects.get(id=curso_id, cv=cv)
        
        context = {
            'curso': curso,
            'es_edicion': True,
        }
        return render(request, 'master/modal_curso.html', context)
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})

def eliminar_curso(request, persona_id, curso_id):
    """
    Vista para eliminar curso de especialización via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            curso = CursoEspecializacion.objects.get(id=curso_id, cv=cv)
            nombre_curso = curso.descripcion
            curso.delete()
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': f'Curso de especialización "{nombre_curso}" eliminado correctamente.'
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    # Para peticiones GET, mostrar modal de confirmación
    try:
        persona = Persona.objects.get(id=persona_id)
        cv = CV.objects.get(persona=persona)
        curso = CursoEspecializacion.objects.get(id=curso_id, cv=cv)
        
        context = {
            'curso': curso,
        }
        return render(request, 'master/modal_eliminar_curso.html', context)
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})

def agregar_experiencia(request, persona_id):
    """
    Vista para agregar experiencia laboral via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            
            # Convertir fechas de string a date
            from datetime import datetime
            fecha_inicio = None
            fecha_fin = None
            
            if request.POST.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            if request.POST.get('fecha_fin'):
                fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            
            experiencia = ExperienciaLaboral.objects.create(
                cv=cv,
                tipo_experiencia=request.POST.get('tipo_experiencia'),
                tipo_entidad=request.POST.get('tipo_entidad'),
                nombre_entidad=request.POST.get('nombre_entidad'),
                cargo=request.POST.get('cargo'),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                salario=request.POST.get('salario') or None,
                motivo_salida=request.POST.get('motivo_salida') or None,
                supervisor=request.POST.get('supervisor') or None,
                telefono_referencia=request.POST.get('telefono_referencia') or None,
                logros=request.POST.get('logros') or None,
                responsabilidades=request.POST.get('responsabilidades') or None,
                observaciones=request.POST.get('observaciones') or None,
            )
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': 'Experiencia laboral agregada correctamente.',
                'experiencia': {
                    'id': experiencia.id,
                    'tipo_experiencia': experiencia.get_tipo_experiencia_display(),
                    'tipo_entidad': experiencia.get_tipo_entidad_display(),
                    'nombre_entidad': experiencia.nombre_entidad,
                    'cargo': experiencia.cargo,
                    'fecha_inicio': experiencia.fecha_inicio.strftime('%Y-%m-%d') if experiencia.fecha_inicio else '',
                    'fecha_fin': experiencia.fecha_fin.strftime('%Y-%m-%d') if experiencia.fecha_fin else '',
                    'salario': str(experiencia.salario) if experiencia.salario else '',
                    'motivo_salida': experiencia.get_motivo_salida_display() if experiencia.motivo_salida else '',
                    'supervisor': experiencia.supervisor or '',
                    'telefono_referencia': experiencia.telefono_referencia or '',
                    'logros': experiencia.logros or '',
                    'responsabilidades': experiencia.responsabilidades or '',
                    'observaciones': experiencia.observaciones or '',
                }
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    return render(request, 'master/modal_experiencia.html')

def editar_experiencia(request, persona_id, experiencia_id):
    """
    Vista para editar experiencia laboral via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            experiencia = ExperienciaLaboral.objects.get(id=experiencia_id, cv=cv)
            
            # Convertir fechas de string a date
            from datetime import datetime
            fecha_inicio = None
            fecha_fin = None
            
            if request.POST.get('fecha_inicio'):
                fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            if request.POST.get('fecha_fin'):
                fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            
            # Actualizar la experiencia
            experiencia.tipo_experiencia = request.POST.get('tipo_experiencia')
            experiencia.tipo_entidad = request.POST.get('tipo_entidad')
            experiencia.nombre_entidad = request.POST.get('nombre_entidad')
            experiencia.cargo = request.POST.get('cargo')
            experiencia.fecha_inicio = fecha_inicio
            experiencia.fecha_fin = fecha_fin
            experiencia.salario = request.POST.get('salario') or None
            experiencia.motivo_salida = request.POST.get('motivo_salida') or None
            experiencia.supervisor = request.POST.get('supervisor') or None
            experiencia.telefono_referencia = request.POST.get('telefono_referencia') or None
            experiencia.logros = request.POST.get('logros') or None
            experiencia.responsabilidades = request.POST.get('responsabilidades') or None
            experiencia.observaciones = request.POST.get('observaciones') or None
            experiencia.save()
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': 'Experiencia laboral actualizada correctamente.',
                'experiencia': {
                    'id': experiencia.id,
                    'tipo_experiencia': experiencia.get_tipo_experiencia_display(),
                    'tipo_entidad': experiencia.get_tipo_entidad_display(),
                    'nombre_entidad': experiencia.nombre_entidad,
                    'cargo': experiencia.cargo,
                    'fecha_inicio': experiencia.fecha_inicio.strftime('%Y-%m-%d') if experiencia.fecha_inicio else '',
                    'fecha_fin': experiencia.fecha_fin.strftime('%Y-%m-%d') if experiencia.fecha_fin else '',
                    'salario': str(experiencia.salario) if experiencia.salario else '',
                    'motivo_salida': experiencia.get_motivo_salida_display() if experiencia.motivo_salida else '',
                    'supervisor': experiencia.supervisor or '',
                    'telefono_referencia': experiencia.telefono_referencia or '',
                    'logros': experiencia.logros or '',
                    'responsabilidades': experiencia.responsabilidades or '',
                    'observaciones': experiencia.observaciones or '',
                }
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    # Para peticiones GET, mostrar el formulario con datos existentes
    try:
        persona = Persona.objects.get(id=persona_id)
        cv = CV.objects.get(persona=persona)
        experiencia = ExperienciaLaboral.objects.get(id=experiencia_id, cv=cv)
        
        context = {
            'experiencia': experiencia,
            'es_edicion': True,
        }
        return render(request, 'master/modal_experiencia.html', context)
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})

def eliminar_experiencia(request, persona_id, experiencia_id):
    """
    Vista para eliminar experiencia laboral via AJAX
    """
    if request.method == 'POST':
        try:
            persona = Persona.objects.get(id=persona_id)
            cv = CV.objects.get(persona=persona)
            experiencia = ExperienciaLaboral.objects.get(id=experiencia_id, cv=cv)
            cargo = experiencia.cargo
            experiencia.delete()
            
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': f'Experiencia laboral "{cargo}" eliminada correctamente.'
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
    
    # Para peticiones GET, mostrar modal de confirmación
    try:
        persona = Persona.objects.get(id=persona_id)
        cv = CV.objects.get(persona=persona)
        experiencia = ExperienciaLaboral.objects.get(id=experiencia_id, cv=cv)
        
        context = {
            'experiencia': experiencia,
        }
        return render(request, 'master/modal_eliminar_experiencia.html', context)
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})

def registrar_colaborador(request, postulacion_id):
    """
    Vista para registrar un colaborador desde una postulación aprobada
    """
    if request.method == 'POST':
        try:
            # Obtener la postulación
            postulacion = get_object_or_404(Postulacion, id=postulacion_id)
            
            # Verificar que la postulación esté aprobada
            if postulacion.estado_postulacion != 'APROBADO':
                return JsonResponse({
                    'success': False, 
                    'errors': {'general': ['Solo se pueden registrar colaboradores de postulaciones aprobadas.']}
                })
            
            # Verificar que la persona no sea ya colaborador
            if hasattr(postulacion.persona, 'colaborador'):
                return JsonResponse({
                    'success': False, 
                    'errors': {'general': ['Esta persona ya es colaborador de la empresa.']}
                })
            
            # Crear el formulario con los datos enviados
            form = ColaboradorForm(request.POST)
            
            if form.is_valid():
                # Crear el colaborador
                colaborador = form.save(commit=False)
                colaborador.persona = postulacion.persona
                
                # Si no se proporciona número de empleado, generar uno automático
                if not colaborador.numero_empleado:
                    # Generar número de empleado automático
                    ultimo_colaborador = Colaborador.objects.filter(
                        numero_empleado__isnull=False
                    ).exclude(numero_empleado='').order_by('-numero_empleado').first()
                    
                    if ultimo_colaborador and ultimo_colaborador.numero_empleado:
                        try:
                            ultimo_numero = int(ultimo_colaborador.numero_empleado.replace('EMP', ''))
                            nuevo_numero = ultimo_numero + 1
                        except (ValueError, AttributeError):
                            nuevo_numero = 1
                    else:
                        nuevo_numero = 1
                    
                    colaborador.numero_empleado = f"EMP{nuevo_numero:03d}"
                
                colaborador.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True, 
                        'message': f'Colaborador registrado exitosamente. Número de empleado: {colaborador.numero_empleado}'
                    })
                
                messages.success(request, f'Colaborador registrado exitosamente. Número de empleado: {colaborador.numero_empleado}')
                return redirect('master:postulantes', convocatoria_id=postulacion.convocatoria.id)
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': form.errors})
                
                messages.error(request, 'Por favor, corrija los errores en el formulario.')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
            
            messages.error(request, f'Error al registrar colaborador: {str(e)}')
            return redirect('master:postulantes', convocatoria_id=postulacion.convocatoria.id)
    
    # Para peticiones GET, devolver el formulario
    try:
        postulacion = get_object_or_404(Postulacion, id=postulacion_id)
        
        # Verificar que la postulación esté aprobada
        if postulacion.estado_postulacion != 'APROBADO':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'errors': {'general': ['Solo se pueden registrar colaboradores de postulaciones aprobadas.']}
                })
            messages.error(request, 'Solo se pueden registrar colaboradores de postulaciones aprobadas.')
            return redirect('master:postulantes', convocatoria_id=postulacion.convocatoria.id)
        
        # Verificar que la persona no sea ya colaborador
        if hasattr(postulacion.persona, 'colaborador'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'errors': {'general': ['Esta persona ya es colaborador de la empresa.']}
                })
            messages.error(request, 'Esta persona ya es colaborador de la empresa.')
            return redirect('master:postulantes', convocatoria_id=postulacion.convocatoria.id)
        
        # Crear formulario con datos iniciales
        form = ColaboradorForm(initial={
            'cargo': postulacion.convocatoria.cargo,
            'fecha_ingreso': timezone.now().date(),
            'estado_laboral': 'ACTIVO',
            'tipo_contrato': 'TIEMPO_COMPLETO',
        })
        
        # Si es petición AJAX, devolver el formulario
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            context = {
                'form': form,
                'postulacion': postulacion,
                'persona': postulacion.persona,
                'convocatoria': postulacion.convocatoria
            }
            html = render_to_string('master/colaborador_create_modal.html', context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        # Para peticiones normales, renderizar página completa
        context = {
            'form': form,
            'postulacion': postulacion,
            'persona': postulacion.persona,
            'convocatoria': postulacion.convocatoria
        }
        return render(request, 'master/colaborador_create.html', context)
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': {'general': [str(e)]}})
        
        messages.error(request, f'Error: {str(e)}')
        return redirect('master:convocatorias')
