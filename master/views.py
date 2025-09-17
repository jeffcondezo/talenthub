from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.utils import timezone
from django.http import Http404
from .forms import CustomLoginForm, PostulacionForm, FormacionAcademicaForm, CursoEspecializacionForm, ExperienciaLaboralForm, PersonaCreateForm
from .models import Persona, Cargo, Area, Convocatoria, Postulacion, FormacionAcademica, CursoEspecializacion, ExperienciaLaboral, CV, Colaborador

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
        
        # Determinar si es aspirante o colaborador
        if hasattr(persona, 'postulaciones'):
            # Es un aspirante
            context['es_aspirante'] = True
            context['es_colaborador'] = False
            
            # Obtener datos del CV del aspirante
            context['formaciones_academicas'] = persona.formaciones_academicas.all().order_by('-fecha_expedicion')
            context['cursos_especializacion'] = persona.cursos_especializacion.all().order_by('-fecha_fin')
            context['experiencias_laborales'] = persona.experiencias_laborales.all().order_by('-fecha_inicio')
            
        else:
            # Es un colaborador
            context['es_aspirante'] = False
            context['es_colaborador'] = True
            
            # Obtener datos del CV del colaborador
            context['formaciones_academicas'] = persona.formaciones_academicas.all().order_by('-fecha_expedicion')
            context['cursos_especializacion'] = persona.cursos_especializacion.all().order_by('-fecha_fin')
            context['experiencias_laborales'] = persona.experiencias_laborales.all().order_by('-fecha_inicio')
        
        # Datos adicionales para el contexto
        context['tipo_persona'] = 'aspirante' if context['es_aspirante'] else 'colaborador'
        context['total_formaciones'] = context['formaciones_academicas'].count()
        context['total_cursos'] = context['cursos_especializacion'].count()
        context['total_experiencias'] = context['experiencias_laborales'].count()
        
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

    def form_valid(self, form):
        """
        Procesar formulario válido
        """
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
    
    def form_valid(self, form):
        """
        Procesar formulario válido
        """
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
        'fecha_inicio_trabajo', 'estado', 'tipo', 'requisitos_minimos',
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


class PersonaCreateView(CreateView):
    """
    Vista basada en clases para crear una nueva persona
    """
    model = Postulacion
    form_class = PersonaCreateForm
    template_name = 'master/aspirante_create.html'
    success_url = reverse_lazy('master:aspirantes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['convocatorias'] = Convocatoria.objects.filter(activo=True).order_by('-fecha_creacion')
        return context

    def form_valid(self, form):
        """
        Procesar formulario válido
        """
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
    model = Postulacion
    template_name = 'master/aspirante_detail.html'
    context_object_name = 'postulacion'
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        postulacion = self.get_object()
        
        # Agregar todas las postulaciones del aspirante
        try:
            context['todas_postulaciones'] = Postulacion.objects.filter(
                aspirante=postulacion.aspirante
            ).select_related('convocatoria__cargo__area').order_by('-fecha_postulacion')
        except Exception:
            context['todas_postulaciones'] = []
        
        return context


class PersonaUpdateView(UpdateView):
    """
    Vista basada en clases para editar una postulación
    """
    model = Postulacion
    form_class = PostulacionForm
    template_name = 'master/aspirante_edit.html'
    context_object_name = 'postulacion'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('master:aspirantes')
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        
        # Agregar opciones para los campos de selección
        try:
            context['estados_choices'] = Postulacion.ESTADO_POSTULACION_CHOICES
        except Exception:
            context['estados_choices'] = []
        
        return context
    
    def form_valid(self, form):
        """
        Procesar formulario válido
        """
        response = super().form_valid(form)
        messages.success(self.request, f'Postulación de "{self.object.aspirante.nombre_completo}" actualizada correctamente.')
        return response
    
    def form_invalid(self, form):
        """
        Procesar formulario inválido
        """
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class PersonaDeleteView(DeleteView):
    """
    Vista basada en clases para eliminar una postulación
    """
    model = Postulacion
    template_name = 'master/aspirante_confirm_delete.html'
    context_object_name = 'postulacion'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('master:aspirantes')
    
    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto
        """
        context = super().get_context_data(**kwargs)
        postulacion = self.get_object()
        
        # Verificar si el aspirante tiene otras postulaciones
        try:
            context['otras_postulaciones'] = Postulacion.objects.filter(
                aspirante=postulacion.aspirante
            ).exclude(id=postulacion.id).count()
        except Exception:
            context['otras_postulaciones'] = 0
        
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Procesar eliminación
        """
        postulacion = self.get_object()
        aspirante_nombre = postulacion.aspirante.nombre_completo
        convocatoria_titulo = postulacion.convocatoria.titulo
        
        # Eliminar la postulación
        postulacion.delete()
        
        # Mensaje de confirmación
        messages.success(
            request, 
            f'Postulación de "{aspirante_nombre}" para "{convocatoria_titulo}" eliminada correctamente.'
        )
        
        # Redirigir a la lista de aspirantes
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
        context['tipo_persona'] = self.kwargs['tipo']
        context['es_edicion'] = False
        
        # Inicializar campos ocultos del formulario
        if self.kwargs['tipo'] == 'aspirante':
            context['form'].fields['aspirante'].initial = self.kwargs['persona_id']
            context['form'].fields['colaborador'].initial = None
        else:
            context['form'].fields['colaborador'].initial = self.kwargs['persona_id']
            context['form'].fields['aspirante'].initial = None
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_formacion_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        formacion = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Formación académica creada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', 
                       tipo=self.kwargs['tipo'], 
                       id=self.kwargs['persona_id'])
    
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
        context['tipo_persona'] = self.kwargs['tipo']
        context['es_edicion'] = True
        
        # Inicializar campos ocultos del formulario
        if self.kwargs['tipo'] == 'aspirante':
            context['form'].fields['aspirante'].initial = self.kwargs['persona_id']
            context['form'].fields['colaborador'].initial = None
        else:
            context['form'].fields['colaborador'].initial = self.kwargs['persona_id']
            context['form'].fields['aspirante'].initial = None
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_formacion_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        formacion = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Formación académica actualizada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', 
                       tipo=self.kwargs['tipo'], 
                       id=self.kwargs['persona_id'])
    
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
        if formacion.aspirante:
            persona_id = formacion.aspirante.id
            tipo = 'aspirante'
        else:
            persona_id = formacion.colaborador.id
            tipo = 'colaborador'
        
        # Eliminar el objeto
        formacion.delete()
        
        # Si es petición AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Formación académica eliminada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', tipo=tipo, id=persona_id)
    
    def get_success_url(self):
        """Redirige al CV después de eliminar"""
        formacion = self.get_object()
        if formacion.aspirante:
            return reverse('master:cv_detail', kwargs={'tipo': 'aspirante', 'id': formacion.aspirante.id})
        else:
            return reverse('master:cv_detail', kwargs={'tipo': 'colaborador', 'id': formacion.colaborador.id})


class CursoEspecializacionCreateView(CreateView):
    """Vista para crear curso de especialización"""
    model = CursoEspecializacion
    form_class = CursoEspecializacionForm
    template_name = 'master/cv_curso_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['tipo_persona'] = self.kwargs['tipo']
        context['es_edicion'] = False
        
        # Inicializar campos ocultos del formulario
        if self.kwargs['tipo'] == 'aspirante':
            context['form'].fields['aspirante'].initial = self.kwargs['persona_id']
            context['form'].fields['colaborador'].initial = None
        else:
            context['form'].fields['colaborador'].initial = self.kwargs['persona_id']
            context['form'].fields['aspirante'].initial = None
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_curso_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        curso = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Curso de especialización creado correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', 
                       tipo=self.kwargs['tipo'], 
                       id=self.kwargs['persona_id'])
    
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
        context['tipo_persona'] = self.kwargs['tipo']
        context['es_edicion'] = True
        
        # Inicializar campos ocultos del formulario
        if self.kwargs['tipo'] == 'aspirante':
            context['form'].fields['aspirante'].initial = self.kwargs['persona_id']
            context['form'].fields['colaborador'].initial = None
        else:
            context['form'].fields['colaborador'].initial = self.kwargs['persona_id']
            context['form'].fields['aspirante'].initial = None
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_curso_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        curso = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Curso de especialización actualizado correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', 
                       tipo=self.kwargs['tipo'], 
                       id=self.kwargs['persona_id'])
    
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
        if curso.aspirante:
            persona_id = curso.aspirante.id
            tipo = 'aspirante'
        else:
            persona_id = curso.colaborador.id
            tipo = 'colaborador'
        
        # Eliminar el objeto
        curso.delete()
        
        # Si es petición AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Curso de especialización eliminado correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', tipo=tipo, id=persona_id)
    
    def get_success_url(self):
        """Redirige al CV después de eliminar"""
        curso = self.get_object()
        if curso.aspirante:
            return reverse('master:cv_detail', kwargs={'tipo': 'aspirante', 'id': curso.aspirante.id})
        else:
            return reverse('master:cv_detail', kwargs={'tipo': 'colaborador', 'id': curso.colaborador.id})


class ExperienciaLaboralCreateView(CreateView):
    """Vista para crear experiencia laboral"""
    model = ExperienciaLaboral
    form_class = ExperienciaLaboralForm
    template_name = 'master/cv_experiencia_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona_id'] = self.kwargs['persona_id']
        context['tipo_persona'] = self.kwargs['tipo']
        context['es_edicion'] = False
        
        # Inicializar campos ocultos del formulario
        if self.kwargs['tipo'] == 'aspirante':
            context['form'].fields['aspirante'].initial = self.kwargs['persona_id']
            context['form'].fields['colaborador'].initial = None
        else:
            context['form'].fields['colaborador'].initial = self.kwargs['persona_id']
            context['form'].fields['aspirante'].initial = None
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_experiencia_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        experiencia = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Experiencia laboral creada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', 
                       tipo=self.kwargs['tipo'], 
                       id=self.kwargs['persona_id'])
    
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
        context['tipo_persona'] = self.kwargs['tipo']
        context['es_edicion'] = True
        
        # Inicializar campos ocultos del formulario
        if self.kwargs['tipo'] == 'aspirante':
            context['form'].fields['aspirante'].initial = self.kwargs['persona_id']
            context['form'].fields['colaborador'].initial = None
        else:
            context['form'].fields['colaborador'].initial = self.kwargs['persona_id']
            context['form'].fields['aspirante'].initial = None
            
        return context
    
    def get_template_names(self):
        """Usa template específico para modales si es petición AJAX"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/cv_experiencia_modal.html']
        return [self.template_name]
    
    def form_valid(self, form):
        """Guarda el formulario"""
        experiencia = form.save()
        
        # Si es petición AJAX, devolver respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Experiencia laboral actualizada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', 
                       tipo=self.kwargs['tipo'], 
                       id=self.kwargs['persona_id'])
    
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
        if experiencia.aspirante:
            persona_id = experiencia.aspirante.id
            tipo = 'aspirante'
        else:
            persona_id = experiencia.colaborador.id
            tipo = 'colaborador'
        
        # Eliminar el objeto
        experiencia.delete()
        
        # Si es petición AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Experiencia laboral eliminada correctamente'})
        
        # Redirigir al CV
        return redirect('master:cv_detail', tipo=tipo, id=persona_id)
    
    def get_success_url(self):
        """Redirige al CV después de eliminar"""
        experiencia = self.get_object()
        if experiencia.aspirante:
            return reverse('master:cv_detail', kwargs={'tipo': 'aspirante', 'id': experiencia.aspirante.id})
        else:
            return reverse('master:cv_detail', kwargs={'tipo': 'colaborador', 'id': experiencia.colaborador.id})
