from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
import json
from .models import PasoInduccion
from django.http import JsonResponse, HttpResponse
from .forms import (
    CustomLoginForm, FormacionAcademicaForm, CursoEspecializacionForm, ExperienciaLaboralForm,
    PostulacionForm, ColaboradorForm, ContratoColaboradorForm, PersonaEditForm,
    PersonaAltaForm, CVPerfilForm, PasswordChangeSpanishForm, UsuarioAccesoForm,
    ActividadSemanalForm, ProyectoForm, AsignacionProyectoForm, validar_archivo_pdf,
)
from .permissions import (
    get_login_redirect_url, get_first_allowed_url, user_is_admin, modulos_labels,
    user_can_manage_persona_cv, get_user_persona, user_has_module,
    user_can_manage_own_actividades, get_or_create_registro_semana,
    semana_iso_desplazada,
)
from .actividades_catalogo import TIPOS_POR_GRUPO, GRUPO_CHOICES
from .actividades_pdf import generar_actividades_semanales_pdf
from functools import wraps
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .models import (
    Persona, Cargo, Area, Convocatoria, Postulacion, FormacionAcademica,
    CursoEspecializacion, ExperienciaLaboral, CV, Colaborador, ContratoColaborador,
    Departamento, Provincia, Distrito, ActividadSemanal, AccesoCVPostulante,
    Proyecto, AsignacionProyecto, PersonaSkill, PerfilAcceso,
)
from .proyecto_matching import (
    rank_colaboradores_por_skills, parse_skills_texto, score_colaborador_contra_skills,
    sync_persona_skills,
)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required # <--- 1. Importa esto


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not user_is_admin(request.user):
            messages.error(request, 'No tiene permiso para acceder a esta sección.')
            return redirect(get_first_allowed_url(request.user))
        return view_func(request, *args, **kwargs)
    return wrapper


def build_cv_context(persona):
    """Contexto compartido para CV virtual (detalle HR y mi-perfil)."""
    cv, _ = CV.objects.get_or_create(persona=persona)
    formaciones = cv.formaciones_academicas.all().order_by('-fecha_expedicion')
    cursos = cv.cursos_especializacion.all().order_by('-fecha_fin')
    experiencias = cv.experiencias_laborales.all().order_by('-fecha_inicio')
    return {
        'cv': cv,
        'formaciones_academicas': formaciones,
        'cursos_especializacion': cursos,
        'experiencias_laborales': experiencias,
        'total_formaciones': formaciones.count(),
        'total_cursos': cursos.count(),
        'total_experiencias': experiencias.count(),
    }


def deny_cv_access_response(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'No autorizado'}, status=403)
    messages.error(request, 'No tiene permiso para acceder a este CV.')
    persona = get_user_persona(request.user)
    if persona:
        return redirect('master:mi_perfil')
    return redirect('master:ajustes')


class CVPersonaAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        persona_id = kwargs.get('persona_id') or kwargs.get('id')
        if persona_id is not None and not user_can_manage_persona_cv(request.user, persona_id):
            return deny_cv_access_response(request)
        return super().dispatch(request, *args, **kwargs)


class CVRecordOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_is_admin(request.user) or user_has_module(request.user, 'colaboradores'):
            return super().dispatch(request, *args, **kwargs)
        persona = get_user_persona(request.user)
        if not persona:
            return deny_cv_access_response(request)
        pk = kwargs.get(self.pk_url_kwarg)
        if pk and not self.model.objects.filter(pk=pk, cv__persona_id=persona.pk).exists():
            return deny_cv_access_response(request)
        return super().dispatch(request, *args, **kwargs)


@login_required
def ajustes_view(request):
    """Vista de ajustes de cuenta: cambio de contraseña."""
    form = PasswordChangeSpanishForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña se actualizó correctamente.')
            return redirect('master:ajustes')
        messages.error(request, 'No se pudo actualizar la contraseña. Revisa los datos ingresados.')

    return render(request, 'master/ajustes.html', {
        'form': form,
        'usuario': request.user,
    })


@login_required
def mi_perfil_view(request):
    """Perfil personal del empleado vinculado a la cuenta."""
    persona = get_user_persona(request.user)
    if persona is None:
        messages.info(
            request,
            'Su cuenta no está vinculada a un empleado. Contacte al administrador.',
        )
        return redirect('master:ajustes')
    context = build_cv_context(persona)
    context['persona'] = persona
    context['es_mi_perfil'] = True
    return render(request, 'master/mi_perfil.html', context)


@login_required # 
def inicio_view(request):
    """Dashboard principal siguiendo el diseño de TalentHub"""
    recientes = Postulacion.objects.select_related('persona', 'convocatoria__cargo').order_by('-fecha_postulacion')[:3]
    
    try:
        nombre_display = request.user.perfil.nombres
    except AttributeError:
        nombre_display = request.user.first_name or request.user.username

    context = {
        'postulantes_activos': Postulacion.objects.filter(estado_postulacion='POSTULADO').count(),
        'total_empleados': Colaborador.objects.filter(estado_laboral='ACTIVO').count(),
        'total_departamentos': Departamento.objects.count(),
        'proyectos_activos_count': 10, 
        
        'postulaciones_recientes': recientes,
        'nombre_usuario': nombre_display
    }
    return render(request, 'master/inicio.html', context)

def induccion_view(request):
    """View para la página de inducción"""
    return render(request, 'master/induccion.html')


def onboarding_view(request):
    # Traemos los pasos de la ruta de bienvenida
    pasos = PasoInduccion.objects.all().order_by('orden')
    return render(request, 'master/induccion.html', {'cursos': pasos})

@login_required
def proyecto_view(request):
    """Listado funcional de proyectos."""
    proyectos = Proyecto.objects.prefetch_related(
        'skills', 'asignaciones', 'asignaciones__colaborador__persona'
    ).annotate(n_asignados=Count('asignaciones', filter=Q(asignaciones__activo=True)))

    estado = request.GET.get('estado', '')
    search = request.GET.get('search', '').strip()
    if estado:
        proyectos = proyectos.filter(estado=estado)
    if search:
        proyectos = proyectos.filter(
            Q(nombre__icontains=search)
            | Q(codigo__icontains=search)
            | Q(cliente__icontains=search)
            | Q(descripcion__icontains=search)
            | Q(skills__nombre__icontains=search)
        ).distinct()

    context = {
        'proyectos': proyectos,
        'total': proyectos.count(),
        'en_curso': Proyecto.objects.filter(estado='EN_CURSO').count(),
        'planificados': Proyecto.objects.filter(estado='PLANIFICADO').count(),
        'finalizados': Proyecto.objects.filter(estado='FINALIZADO').count(),
        'estado': estado,
        'search': search,
        'estado_choices': Proyecto.ESTADO_CHOICES,
    }
    return render(request, 'master/proyectos.html', context)


@login_required
def proyecto_create(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creado_por = request.user
            proyecto.save()
            form.sync_skills(proyecto)
            messages.success(request, f'Proyecto {proyecto.codigo} creado.')
            return redirect('master:proyecto_detail', pk=proyecto.pk)
    else:
        form = ProyectoForm()

    sugeridos = []
    skills_preview = parse_skills_texto(request.GET.get('skills', ''))
    if skills_preview:
        sugeridos = rank_colaboradores_por_skills(skills_preview)[:12]

    return render(request, 'master/proyecto_form.html', {
        'form': form,
        'titulo': 'Nuevo proyecto',
        'modo': 'create',
        'sugeridos': sugeridos,
        'skills_preview': ', '.join(skills_preview),
    })


@login_required
def proyecto_edit(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            form.sync_skills(proyecto)
            messages.success(request, 'Proyecto actualizado.')
            return redirect('master:proyecto_detail', pk=proyecto.pk)
    else:
        form = ProyectoForm(instance=proyecto)

    return render(request, 'master/proyecto_form.html', {
        'form': form,
        'titulo': f'Editar {proyecto.codigo}',
        'modo': 'edit',
        'proyecto': proyecto,
        'sugeridos': [],
        'skills_preview': '',
    })


@login_required
def proyecto_detail(request, pk):
    proyecto = get_object_or_404(
        Proyecto.objects.prefetch_related(
            'skills',
            'asignaciones__colaborador__persona',
            'asignaciones__colaborador__cargo',
        ),
        pk=pk,
    )
    asignaciones = list(proyecto.asignaciones.select_related(
        'colaborador__persona', 'colaborador__cargo'
    ))
    skills = list(proyecto.skills.all())
    excluidos = [a.colaborador_id for a in asignaciones if a.activo]
    sugeridos = rank_colaboradores_por_skills(skills, exclude_ids=excluidos)[:15]

    for a in asignaciones:
        a.match_meta = score_colaborador_contra_skills(a.colaborador, skills)

    form_asignacion = AsignacionProyectoForm(proyecto=proyecto)

    return render(request, 'master/proyecto_detail.html', {
        'proyecto': proyecto,
        'asignaciones': asignaciones,
        'skills': skills,
        'sugeridos': sugeridos,
        'form_asignacion': form_asignacion,
        'horas_asignadas': proyecto.horas_asignadas_total,
    })


@login_required
def proyecto_delete(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        codigo = proyecto.codigo
        proyecto.delete()
        messages.success(request, f'Proyecto {codigo} eliminado.')
        return redirect('master:proyecto')
    return render(request, 'master/proyecto_confirm_delete.html', {'proyecto': proyecto})


@login_required
def proyecto_asignar(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method != 'POST':
        return redirect('master:proyecto_detail', pk=pk)

    form = AsignacionProyectoForm(request.POST, proyecto=proyecto)
    if form.is_valid():
        asignacion = form.save(commit=False)
        asignacion.proyecto = proyecto
        asignacion.save()
        messages.success(
            request,
            f'{asignacion.colaborador.persona.nombre_completo} asignado '
            f'({asignacion.horas_semanales} h/sem).',
        )
    else:
        messages.error(request, 'No se pudo asignar: revise el formulario.')
    return redirect('master:proyecto_detail', pk=pk)


@login_required
def proyecto_asignacion_edit(request, pk, asignacion_id):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    asignacion = get_object_or_404(AsignacionProyecto, pk=asignacion_id, proyecto=proyecto)
    if request.method == 'POST':
        form = AsignacionProyectoForm(request.POST, instance=asignacion, proyecto=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignación actualizada.')
            return redirect('master:proyecto_detail', pk=pk)
    else:
        form = AsignacionProyectoForm(instance=asignacion, proyecto=proyecto)

    return render(request, 'master/proyecto_asignacion_form.html', {
        'form': form,
        'proyecto': proyecto,
        'asignacion': asignacion,
    })


@login_required
def proyecto_asignacion_quitar(request, pk, asignacion_id):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    asignacion = get_object_or_404(AsignacionProyecto, pk=asignacion_id, proyecto=proyecto)
    if request.method == 'POST':
        nombre = asignacion.colaborador.persona.nombre_completo
        asignacion.delete()
        messages.success(request, f'{nombre} fue quitado del proyecto.')
    return redirect('master:proyecto_detail', pk=pk)


@login_required
def proyecto_sugerir_recursos(request):
    """AJAX: sugiere colaboradores según skills (texto o ids de proyecto)."""
    skills_texto = request.GET.get('skills', '').strip()
    proyecto_id = request.GET.get('proyecto_id')
    skills = []

    if proyecto_id:
        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
        skills = list(proyecto.skills.all())
        excluidos = list(
            proyecto.asignaciones.filter(activo=True).values_list('colaborador_id', flat=True)
        )
    else:
        skills = parse_skills_texto(skills_texto)
        excluidos = []

    if not skills:
        return JsonResponse({'success': True, 'resultados': []})

    ranked = rank_colaboradores_por_skills(skills, exclude_ids=excluidos)[:20]
    data = []
    for r in ranked:
        p = r['persona']
        data.append({
            'colaborador_id': r['colaborador'].id,
            'persona_id': p.id,
            'nombre': p.nombre_completo,
            'cargo': r['colaborador'].cargo.nombre if r['colaborador'].cargo_id else '',
            'score': r['score'],
            'matched': r['matched'],
            'missing': r['missing'],
            'horas_otras': r['horas_otras'],
            'perfil_url': reverse('master:persona_detail', kwargs={'id': p.id}),
        })
    return JsonResponse({'success': True, 'resultados': data})


def perfiles_view(request):
    """View para la página de perfiles"""
    return render(request, 'master/perfiles.html')

def capacitacion_view(request):
    """View para la página de capacitación con filtros sobre CursoEspecializacion"""
    cursos = CursoEspecializacion.objects.select_related('cv', 'cv__persona').all()

    # filtros
    tipo = request.GET.get('tipo_estudio')
    nivel = request.GET.get('nivel')
    pais = request.GET.get('pais')
    ciudad = request.GET.get('ciudad')
    institucion = request.GET.get('institucion')
    search = request.GET.get('search')

    if tipo:
        cursos = cursos.filter(tipo_estudio=tipo)
    if nivel:
        cursos = cursos.filter(nivel=nivel)
    if pais:
        cursos = cursos.filter(pais__icontains=pais)
    if ciudad:
        cursos = cursos.filter(ciudad__icontains=ciudad)
    if institucion:
        cursos = cursos.filter(institucion__icontains=institucion)
    if search:
        cursos = cursos.filter(
            Q(descripcion__icontains=search) |
            Q(institucion__icontains=search) |
            Q(ciudad__icontains=search) |
            Q(pais__icontains=search)
        )

    context = {
        'cursos': cursos,
        'tipos': CursoEspecializacion.TIPO_ESTUDIO_CHOICES,
        'niveles': CursoEspecializacion.NIVEL_CHOICES,
        'filters': {
            'tipo_estudio': tipo or '',
            'nivel': nivel or '',
            'pais': pais or '',
            'ciudad': ciudad or '',
            'institucion': institucion or '',
            'search': search or ''
        }
    }

    return render(request, 'master/capacitacion.html', context)


@login_required
def analitica_view(request):
    """Analíticas con datos reales: reclutamiento, áreas, proyectos y skills."""
    MES_ES = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic',
    }

    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    inicio_mes_ant = (inicio_mes - timedelta(days=1)).replace(day=1)

    empleados_activos = Colaborador.objects.filter(estado_laboral='ACTIVO').count()
    empleados_total = Colaborador.objects.count()
    empleados_mes = Colaborador.objects.filter(fecha_ingreso__gte=inicio_mes).count()
    empleados_mes_ant = Colaborador.objects.filter(
        fecha_ingreso__gte=inicio_mes_ant, fecha_ingreso__lt=inicio_mes
    ).count()

    postulaciones_total = Postulacion.objects.count()
    postulaciones_mes = Postulacion.objects.filter(fecha_postulacion__date__gte=inicio_mes).count()
    postulaciones_mes_ant = Postulacion.objects.filter(
        fecha_postulacion__date__gte=inicio_mes_ant,
        fecha_postulacion__date__lt=inicio_mes,
    ).count()
    postulantes_unicos = Postulacion.objects.exclude(persona__isnull=True).values('persona').distinct().count()

    aprobados = Postulacion.objects.filter(estado_postulacion='APROBADO').count()
    tasa_aprobacion = round((aprobados * 100.0 / postulaciones_total), 1) if postulaciones_total else 0

    convocatorias_activas = Convocatoria.objects.filter(
        estado__in=['PUBLICADA', 'EN_PROCESO'], activo=True
    ).count()
    proyectos_en_curso = Proyecto.objects.filter(estado='EN_CURSO').count()
    proyectos_total = Proyecto.objects.count()
    personas_con_skills = PersonaSkill.objects.values('persona').distinct().count()
    horas_proyecto = AsignacionProyecto.objects.filter(activo=True).aggregate(
        t=Sum('horas_semanales')
    )['t'] or 0

    def delta_txt(actual, anterior):
        if anterior == 0:
            return f'+{actual}' if actual else '0'
        diff = actual - anterior
        pct = round((diff * 100.0) / anterior, 1)
        sign = '+' if pct >= 0 else ''
        return f'{sign}{pct}%'

    summaries = [
        {
            'title': 'Empleados activos',
            'value': empleados_activos,
            'delta': delta_txt(empleados_mes, empleados_mes_ant),
            'hint': f'{empleados_total} en total · ingresos del mes',
            'icon': 'fa-users',
        },
        {
            'title': 'Postulaciones',
            'value': postulaciones_total,
            'delta': delta_txt(postulaciones_mes, postulaciones_mes_ant),
            'hint': f'{postulantes_unicos} personas únicas',
            'icon': 'fa-user-plus',
        },
        {
            'title': 'Tasa de aprobación',
            'value': f'{tasa_aprobacion}%',
            'delta': f'{aprobados} aprobados',
            'hint': 'Sobre total de postulaciones',
            'icon': 'fa-check-circle',
        },
        {
            'title': 'Proyectos en curso',
            'value': proyectos_en_curso,
            'delta': f'{proyectos_total} totales',
            'hint': f'{horas_proyecto} h/sem asignadas',
            'icon': 'fa-briefcase',
        },
    ]

    # Últimos 6 meses
    meses = []
    y, m = hoy.year, hoy.month
    for _ in range(6):
        meses.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    meses = list(reversed(meses))
    desde = date(meses[0][0], meses[0][1], 1)

    posts_por_mes = {
        (row['periodo'].year, row['periodo'].month): row['n']
        for row in (
            Postulacion.objects.filter(fecha_postulacion__date__gte=desde)
            .annotate(periodo=TruncMonth('fecha_postulacion'))
            .values('periodo')
            .annotate(n=Count('id'))
        )
        if row['periodo']
    }
    ingresos_por_mes = {
        (row['periodo'].year, row['periodo'].month): row['n']
        for row in (
            Colaborador.objects.filter(fecha_ingreso__gte=desde)
            .annotate(periodo=TruncMonth('fecha_ingreso'))
            .values('periodo')
            .annotate(n=Count('id'))
        )
        if row['periodo']
    }

    applicants = [posts_por_mes.get(key, 0) for key in meses]
    hired = [ingresos_por_mes.get(key, 0) for key in meses]
    max_app = max(applicants) if any(applicants) else 1
    max_hired = max(hired) if any(hired) else 1
    recruitment_trend = {
        'labels': [MES_ES[m] for _, m in meses],
        'applicants': applicants,
        'hired': hired,
        'bars': [
            {
                'label': MES_ES[m],
                'applicants': applicants[i],
                'hired': hired[i],
                'app_pct': int(round(applicants[i] * 100.0 / max_app)) if max_app else 0,
                'hired_pct': int(round(hired[i] * 100.0 / max_hired)) if max_hired else 0,
            }
            for i, (_, m) in enumerate(meses)
        ],
    }

    estado_map = dict(Postulacion.ESTADO_POSTULACION_CHOICES)
    pipeline_counts = {
        row['estado_postulacion']: row['n']
        for row in Postulacion.objects.values('estado_postulacion').annotate(n=Count('id'))
    }
    total_pipeline = sum(pipeline_counts.values()) or 0
    pipeline = []
    for key, label in Postulacion.ESTADO_POSTULACION_CHOICES:
        count = pipeline_counts.get(key, 0)
        percent = int(round(count * 100.0 / total_pipeline)) if total_pipeline else 0
        pipeline.append({'name': label, 'count': count, 'percent': percent})

    # Empleados por área
    area_rows = (
        Colaborador.objects.filter(estado_laboral='ACTIVO', cargo__area__isnull=False)
        .values('cargo__area__nombre')
        .annotate(n=Count('id'))
        .order_by('-n')
    )
    area_total = sum(r['n'] for r in area_rows) or 0
    departments_pairs = [
        {
            'label': r['cargo__area__nombre'],
            'count': r['n'],
            'percent': int(round(r['n'] * 100.0 / area_total)) if area_total else 0,
        }
        for r in area_rows
    ]

    # Estado laboral
    laboral_pairs = [
        {
            'label': dict(Colaborador.ESTADO_LABORAL_CHOICES).get(r['estado_laboral'], r['estado_laboral']),
            'count': r['n'],
        }
        for r in Colaborador.objects.values('estado_laboral').annotate(n=Count('id')).order_by('-n')
    ]

    # Proyectos
    proy_estado = [
        {
            'label': dict(Proyecto.ESTADO_CHOICES).get(r['estado'], r['estado']),
            'count': r['n'],
        }
        for r in Proyecto.objects.values('estado').annotate(n=Count('id')).order_by('-n')
    ]
    top_proyectos = (
        Proyecto.objects.annotate(
            n_equipo=Count('asignaciones', filter=Q(asignaciones__activo=True)),
            horas=Sum('asignaciones__horas_semanales', filter=Q(asignaciones__activo=True)),
        )
        .order_by('-n_equipo', '-horas')[:8]
    )
    puntaje_promedio = Postulacion.objects.exclude(puntaje__isnull=True).aggregate(
        avg=Avg('puntaje')
    )['avg']
    puntaje_promedio = round(puntaje_promedio, 1) if puntaje_promedio is not None else None

    # Skills y formación
    top_skills = list(
        PersonaSkill.objects.values('skill__nombre')
        .annotate(n=Count('id'))
        .order_by('-n')[:10]
    )
    max_skill = top_skills[0]['n'] if top_skills else 1
    for s in top_skills:
        s['percent'] = int(round(s['n'] * 100.0 / max_skill)) if max_skill else 0

    cursos_total = CursoEspecializacion.objects.count()
    formaciones_total = FormacionAcademica.objects.count()
    cvs_con_archivo = CV.objects.exclude(cv_archivo='').exclude(cv_archivo__isnull=True).count()

    context = {
        'summaries': summaries,
        'recruitment_trend': recruitment_trend,
        'pipeline': pipeline,
        'departments_pairs': departments_pairs,
        'laboral_pairs': laboral_pairs,
        'proy_estado': proy_estado,
        'top_proyectos': top_proyectos,
        'puntaje_promedio': puntaje_promedio,
        'top_skills': top_skills,
        'cursos_total': cursos_total,
        'formaciones_total': formaciones_total,
        'personas_con_skills': personas_con_skills,
        'cvs_con_archivo': cvs_con_archivo,
        'convocatorias_activas': convocatorias_activas,
        'horas_proyecto': horas_proyecto,
    }
    return render(request, 'master/analitica.html', context)

class CVDetailView(CVPersonaAccessMixin, DetailView):
    """
    Vista basada en clases para mostrar el CV completo de una persona
    """
    template_name = 'master/cv_detail.html'
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
        context.update(build_cv_context(persona))
        context['colaborador'] = getattr(persona, 'colaborador', None)
        context['tiene_postulaciones'] = persona.postulaciones.exists()
        context['es_colaborador'] = context['colaborador'] is not None
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

        # Personas aún no postuladas a esta convocatoria (para el modal)
        ya_postuladas = Postulacion.objects.filter(
            convocatoria_id=convocatoria_id
        ).values_list('persona_id', flat=True)
        context['personas_disponibles'] = Persona.objects.exclude(
            id__in=ya_postuladas
        ).order_by('apellido_paterno', 'nombres')[:200]

        return context


def _anio_de_fecha(valor):
    if not valor:
        return None
    return valor.year if hasattr(valor, 'year') else None


def _metricas_postulante(postulacion):
    """Calcula indicadores comparables a partir del CV de la persona."""
    persona = postulacion.persona
    cv = None
    if persona is not None:
        try:
            cv = persona.cv
        except CV.DoesNotExist:
            cv = None

    formaciones = list(cv.formaciones_academicas.all()) if cv else []
    cursos = list(cv.cursos_especializacion.all()) if cv else []
    experiencias = list(cv.experiencias_laborales.all()) if cv else []

    anios_exp_cv = 0
    for exp in experiencias:
        if not exp.fecha_inicio:
            continue
        fin = exp.fecha_fin or timezone.now().date()
        if fin >= exp.fecha_inicio:
            anios_exp_cv += max((fin - exp.fecha_inicio).days / 365.25, 0)
    anios_exp_cv = round(anios_exp_cv, 1)
    anios_exp = max(postulacion.experiencia_anios or 0, int(anios_exp_cv))

    anios_formacion = [
        y for y in (
            _anio_de_fecha(f.fecha_fin) or _anio_de_fecha(f.fecha_expedicion)
            for f in formaciones
        ) if y
    ]
    anios_cursos = [y for y in (_anio_de_fecha(c.fecha_fin) for c in cursos) if y]

    ultimo_formacion = max(anios_formacion) if anios_formacion else None
    ultimo_curso = max(anios_cursos) if anios_cursos else None

    tiene_cv_archivo = bool(cv and (cv.cv_archivo or cv.cv_archivo_anexos))
    docs_adjuntos = 0
    if cv and cv.cv_archivo:
        docs_adjuntos += 1
    if cv and cv.cv_archivo_anexos:
        docs_adjuntos += 1
    docs_adjuntos += sum(1 for f in formaciones if f.archivo)
    docs_adjuntos += sum(1 for c in cursos if c.certificado)
    docs_adjuntos += sum(1 for e in experiencias if e.archivo)

    return {
        'postulacion': postulacion,
        'persona': persona,
        'cv': cv,
        'anios_experiencia': anios_exp,
        'n_formaciones': len(formaciones),
        'n_cursos': len(cursos),
        'ultimo_formacion': ultimo_formacion,
        'ultimo_curso': ultimo_curso,
        'tiene_cv_archivo': tiene_cv_archivo,
        'docs_adjuntos': docs_adjuntos,
        'nivel_educacion': postulacion.nivel_educacion or '',
        'score': postulacion.puntaje,
        'estado': postulacion.estado_postulacion,
        'estado_display': postulacion.get_estado_postulacion_display(),
    }


@login_required
def comparar_postulantes(request, convocatoria_id):
    """Dashboard para comparar postulantes de una convocatoria."""
    convocatoria = get_object_or_404(
        Convocatoria.objects.select_related('cargo', 'cargo__area'),
        pk=convocatoria_id,
    )
    postulaciones = (
        Postulacion.objects.filter(convocatoria=convocatoria)
        .select_related('persona', 'persona__cv')
        .prefetch_related(
            'persona__cv__formaciones_academicas',
            'persona__cv__cursos_especializacion',
            'persona__cv__experiencias_laborales',
        )
    )

    estado = request.GET.get('estado', '')
    if estado:
        postulaciones = postulaciones.filter(estado_postulacion=estado)

    search = request.GET.get('search', '').strip()
    if search:
        postulaciones = postulaciones.filter(
            Q(persona__nombres__icontains=search)
            | Q(persona__apellido_paterno__icontains=search)
            | Q(persona__apellido_materno__icontains=search)
            | Q(persona__numero_documento__icontains=search)
            | Q(persona__email__icontains=search)
        )

    candidatos = [_metricas_postulante(p) for p in postulaciones if p.persona_id]

    orden = request.GET.get('orden', 'score')
    dir_param = request.GET.get('dir', 'desc')
    reverse = dir_param != 'asc'
    key_map = {
        'score': lambda c: (c['score'] is not None, c['score'] or 0),
        'experiencia': lambda c: c['anios_experiencia'] or 0,
        'formacion': lambda c: c['n_formaciones'] or 0,
        'ultimo_formacion': lambda c: c['ultimo_formacion'] or 0,
        'cursos': lambda c: c['n_cursos'] or 0,
        'ultimo_curso': lambda c: c['ultimo_curso'] or 0,
        'cv': lambda c: (1 if c['tiene_cv_archivo'] else 0, c['docs_adjuntos'] or 0),
        'nombre': lambda c: (
            (c['persona'].apellido_paterno or '').lower(),
            (c['persona'].nombres or '').lower(),
        ),
        'estado': lambda c: c['estado'] or '',
    }
    if orden not in key_map:
        orden = 'score'
    candidatos.sort(key=key_map[orden], reverse=reverse)

    for i, c in enumerate(candidatos, start=1):
        c['rank'] = i

    top_exp = max((c['anios_experiencia'] for c in candidatos), default=0)
    top_form = max((c['n_formaciones'] for c in candidatos), default=0)
    top_cursos = max((c['n_cursos'] for c in candidatos), default=0)

    def sort_url(campo):
        nueva_dir = 'asc' if (orden == campo and dir_param == 'desc') else 'desc'
        if orden != campo:
            nueva_dir = 'desc'
        from urllib.parse import urlencode
        params = {'orden': campo, 'dir': nueva_dir}
        if search:
            params['search'] = search
        if estado:
            params['estado'] = estado
        return f'?{urlencode(params)}'

    context = {
        'convocatoria': convocatoria,
        'candidatos': candidatos,
        'total': len(candidatos),
        'top_experiencia': top_exp,
        'top_formaciones': top_form,
        'top_cursos': top_cursos,
        'estado': estado,
        'search': search,
        'orden': orden,
        'dir': 'desc' if reverse else 'asc',
        'estado_choices': Postulacion.ESTADO_POSTULACION_CHOICES,
        'promedio_experiencia': round(
            sum(c['anios_experiencia'] for c in candidatos) / len(candidatos), 1
        ) if candidatos else 0,
        'sort_urls': {
            'nombre': sort_url('nombre'),
            'cv': sort_url('cv'),
            'experiencia': sort_url('experiencia'),
            'formacion': sort_url('formacion'),
            'ultimo_formacion': sort_url('ultimo_formacion'),
            'cursos': sort_url('cursos'),
            'ultimo_curso': sort_url('ultimo_curso'),
            'score': sort_url('score'),
            'estado': sort_url('estado'),
        },
    }
    return render(request, 'master/comparar_postulantes.html', context)


@login_required
def actualizar_estado_postulacion_ajax(request, pk):
    """Cambia el estado/fase de una postulación desde el dashboard."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'errors': {'general': ['Método no permitido']}}, status=405)

    postulacion = get_object_or_404(Postulacion, pk=pk)
    estado = request.POST.get('estado') or request.POST.get('estado_postulacion')
    validos = {k for k, _ in Postulacion.ESTADO_POSTULACION_CHOICES}
    # Compatibilidad con datos legacy guardados con etiqueta en español
    label_to_code = {label: code for code, label in Postulacion.ESTADO_POSTULACION_CHOICES}
    if estado in label_to_code:
        estado = label_to_code[estado]
    if estado not in validos:
        return JsonResponse({'success': False, 'errors': {'general': ['Estado inválido']}}, status=400)

    postulacion.estado_postulacion = estado
    postulacion.save(update_fields=['estado_postulacion', 'fecha_actualizacion'])
    return JsonResponse({
        'success': True,
        'estado': postulacion.estado_postulacion,
        'estado_display': postulacion.get_estado_postulacion_display(),
    })


@login_required
def actualizar_puntaje_postulacion_ajax(request, pk):
    """Asigna o actualiza el puntaje manual de una postulación."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'errors': {'general': ['Método no permitido']}}, status=405)

    postulacion = get_object_or_404(Postulacion, pk=pk)
    raw = request.POST.get('puntaje', '').strip()
    if raw == '':
        postulacion.puntaje = None
    else:
        try:
            valor = int(raw)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'errors': {'general': ['Puntaje inválido']}}, status=400)
        if valor < 0 or valor > 1000:
            return JsonResponse({'success': False, 'errors': {'general': ['Use un valor entre 0 y 1000']}}, status=400)
        postulacion.puntaje = valor

    postulacion.save(update_fields=['puntaje', 'fecha_actualizacion'])
    return JsonResponse({
        'success': True,
        'puntaje': postulacion.puntaje,
    })


class PersonaCreateView(CreateView):
    """
    Vista basada en clases para crear una nueva persona
    """
    model = Persona
    form_class = PersonaAltaForm
    template_name = 'master/persona_create.html'
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
            return JsonResponse({
                'success': True,
                'message': 'Persona creada correctamente',
                'persona_id': self.object.pk,
            })

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

        try:
            context['acceso_cv'] = persona.acceso_cv
        except AccesoCVPostulante.DoesNotExist:
            context['acceso_cv'] = None

        persona_skills = list(
            persona.persona_skills.select_related('skill').order_by('skill__nombre')
        )
        context['persona_skills'] = persona_skills
        context['persona_skills_texto'] = ', '.join(ps.skill.nombre for ps in persona_skills)

        return context


@login_required
def persona_skills_update(request, id):
    """Registra/actualiza skills evaluados de una persona (match con proyectos)."""
    persona = get_object_or_404(Persona, pk=id)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'errors': {'general': ['Método no permitido']}}, status=405)

    skills_texto = request.POST.get('skills_texto', '')
    items = sync_persona_skills(persona, skills_texto, user=request.user)
    data = {
        'success': True,
        'message': f'{len(items)} skill(s) registrados.',
        'skills': [{'id': ps.skill_id, 'nombre': ps.skill.nombre} for ps in items],
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(data)
    messages.success(request, data['message'])
    return redirect('master:persona_detail', id=persona.id)


@login_required
def cv_perfil_edit(request, id):
    """Editar perfil y trayectoria profesional (CV) de una persona."""
    persona = get_object_or_404(Persona, id=id)
    if not user_can_manage_persona_cv(request.user, persona.id):
        return deny_cv_access_response(request)

    cv, _created = CV.objects.get_or_create(persona=persona)
    es_mi_perfil = (
        get_user_persona(request.user) is not None
        and request.user.perfil.pk == persona.pk
    )

    if request.method == 'POST':
        form = CVPerfilForm(request.POST, request.FILES, instance=cv)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil profesional actualizado correctamente.')
            if es_mi_perfil:
                return redirect('master:mi_perfil')
            return redirect('master:persona_detail', id=persona.id)
    else:
        form = CVPerfilForm(instance=cv)

    return render(request, 'master/persona_cv_perfil_edit.html', {
        'persona': persona,
        'cv': cv,
        'form': form,
        'es_mi_perfil': es_mi_perfil,
    })


def colaborador_empleo_edit(request, id):
    """Editar o registrar datos de empleo de un colaborador."""
    persona = get_object_or_404(Persona, id=id)
    colaborador = Colaborador.objects.select_related('cargo').filter(persona=persona).first()
    es_nuevo = colaborador is None
    puede_registrar_contratos = colaborador is not None
    redirect_url = reverse('master:persona_empleo_edit', kwargs={'id': persona.id})

    if request.method == 'POST':
        accion = request.POST.get('accion', 'empleo')

        if accion == 'eliminar_contrato' and colaborador:
            contrato_id = request.POST.get('contrato_id')
            contrato = get_object_or_404(
                ContratoColaborador,
                pk=contrato_id,
                colaborador=colaborador,
            )
            contrato.delete()
            messages.success(request, 'Contrato eliminado correctamente.')
            return redirect(redirect_url)

        if accion == 'contrato' and colaborador:
            contrato_form = ContratoColaboradorForm(request.POST, request.FILES)
            if contrato_form.is_valid():
                contrato = contrato_form.save(commit=False)
                contrato.colaborador = colaborador
                contrato.save()
                messages.success(request, 'Contrato registrado correctamente.')
                return redirect(redirect_url)
            form = ColaboradorForm(instance=colaborador)
            contratos = colaborador.contratos.all()
        else:
            contrato_form = ContratoColaboradorForm()
            form = ColaboradorForm(request.POST, instance=colaborador)
            if form.is_valid():
                colaborador_actualizado = form.save(commit=False)
                colaborador_actualizado.persona = persona
                colaborador_actualizado.save()
                if es_nuevo:
                    from .aprender_services import asignar_ruta_induccion
                    n_cursos = len(asignar_ruta_induccion(colaborador_actualizado))
                    extra = f' Se asignaron {n_cursos} curso(s) de inducción.' if n_cursos else ''
                    messages.success(
                        request,
                        f'Colaborador registrado correctamente.{extra}',
                    )
                    return redirect('master:colaboradores')
                messages.success(request, 'Datos de empleo actualizados correctamente.')
                return redirect('master:persona_detail', id=persona.id)
            contratos = colaborador.contratos.all() if colaborador else []
    else:
        contrato_form = ContratoColaboradorForm()
        if colaborador:
            form = ColaboradorForm(instance=colaborador)
            contratos = colaborador.contratos.all()
        else:
            form = ColaboradorForm(initial={
                'fecha_ingreso': timezone.now().date(),
                'estado_laboral': 'ACTIVO',
                'tipo_contrato': 'TIEMPO_COMPLETO',
            })
            contratos = []

    form.fields['cargo'].queryset = Cargo.objects.filter(activo=True).select_related('area')
    supervisor_qs = Colaborador.objects.select_related('persona')
    if colaborador:
        supervisor_qs = supervisor_qs.exclude(pk=colaborador.pk)
    form.fields['supervisor'].queryset = supervisor_qs
    form.fields['supervisor'].required = False
    form.fields['supervisor'].empty_label = 'Sin supervisor'

    return render(request, 'master/persona_colaborador_empleo_edit.html', {
        'persona': persona,
        'colaborador': colaborador,
        'form': form,
        'contrato_form': contrato_form,
        'contratos': contratos,
        'es_nuevo': es_nuevo,
        'puede_registrar_contratos': puede_registrar_contratos,
    })


class PersonaUpdateView(UpdateView):
    """
    Vista basada en clases para editar una persona
    """
    model = Persona
    form_class = PersonaEditForm
    template_name = 'master/persona_edit.html'
    context_object_name = 'persona'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('master:personas')

    def get_success_url(self):
        return reverse('master:persona_detail', kwargs={'id': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            kwargs['cv'] = self.get_object().cv
        except CV.DoesNotExist:
            kwargs['cv'] = None
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cv'] = self.object.cv
        except CV.DoesNotExist:
            context['cv'] = None
        return context
    
    def get(self, request, *args, **kwargs):
        """Mostrar formulario de edición"""
        # Si es petición AJAX, devolver solo el contenido del modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            # Establecer el objeto primero
            self.object = self.get_object()
            context = self.get_context_data()
            html = render_to_string('master/persona_edit_form.html', context, request=request)
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
        queryset = Convocatoria.objects.select_related(
            'cargo__area'
        ).annotate(
            total_postulaciones=Count('postulaciones')
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
    colaboradores_qs = Colaborador.objects.select_related('persona', 'cargo', 'cargo__area').all()

    search = request.GET.get('search')
    if search:
        colaboradores_qs = colaboradores_qs.filter(
            Q(persona__nombres__icontains=search) |
            Q(persona__apellido_paterno__icontains=search) |
            Q(persona__apellido_materno__icontains=search) |
            Q(persona__numero_documento__icontains=search) |
            Q(persona__email__icontains=search) |
            Q(cargo__nombre__icontains=search) |
            Q(numero_empleado__icontains=search)
        )

    estado = request.GET.get('estado')
    if estado:
        colaboradores_qs = colaboradores_qs.filter(estado_laboral=estado)

    tipo = request.GET.get('tipo')
    if tipo:
        colaboradores_qs = colaboradores_qs.filter(tipo_contrato=tipo)

    cargo = request.GET.get('cargo')
    if cargo:
        colaboradores_qs = colaboradores_qs.filter(cargo_id=cargo)

    area = request.GET.get('area')
    if area:
        colaboradores_qs = colaboradores_qs.filter(cargo__area_id=area)

    context = {
        'colaboradores': colaboradores_qs,
        'total_colaboradores': colaboradores_qs.count(),
        'colaboradores_activos': colaboradores_qs.filter(estado_laboral='ACTIVO').count(),
        'cargos': Cargo.objects.filter(activo=True).select_related('area'),
        'areas': Area.objects.filter(activo=True),
    }
    return render(request, 'master/colaboradores.html', context)


def eliminar_colaborador(request, id):
    """Eliminar un colaborador por id. Responde JSON para peticiones AJAX."""
    from django.views.decorators.http import require_POST
    from django.http import JsonResponse

    if request.method == 'POST':
        try:
            colaborador = Colaborador.objects.get(id=id)
            colaborador.delete()
            return JsonResponse({'success': True, 'message': 'Colaborador eliminado'})
        except Colaborador.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Colaborador no encontrado'}, status=404)
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

class CustomLoginView(LoginView):
    template_name = 'master/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Si el usuario solo está entrando a la página (GET), 
        # forzamos a que no existan datos para validar.
        if self.request.method == 'GET':
            kwargs['data'] = None
            kwargs['files'] = None
        return kwargs

    def get_success_url(self):
        return get_login_redirect_url(self.request.user)

    def form_invalid(self, form):
        # Solo añadimos el mensaje de error si el usuario REALMENTE intentó loguearse
        # if self.request.method == 'POST':
          #  messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)

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
    
    def form_valid(self, form):
        """Elimina la convocatoria (Django 4.2+ usa form_valid en DeleteView)."""
        convocatoria = self.object
        titulo = convocatoria.titulo
        total_postulaciones = convocatoria.postulaciones.count()
        convocatoria.delete()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Convocatoria "{titulo}" eliminada correctamente',
            })

        if total_postulaciones > 0:
            messages.success(
                self.request,
                f'Convocatoria "{titulo}" eliminada correctamente. '
                f'Se eliminaron {total_postulaciones} postulaciones relacionadas.',
            )
        else:
            messages.success(self.request, f'Convocatoria "{titulo}" eliminada correctamente.')
        return redirect(self.success_url)


# ===== VISTAS PARA GESTIÓN DE CV =====

class FormacionAcademicaCreateView(CVPersonaAccessMixin, CreateView):
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


class FormacionAcademicaUpdateView(CVPersonaAccessMixin, UpdateView):
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


class FormacionAcademicaDeleteView(CVRecordOwnerMixin, DeleteView):
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


class CursoEspecializacionCreateView(CVPersonaAccessMixin, CreateView):
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


class CursoEspecializacionUpdateView(CVPersonaAccessMixin, UpdateView):
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


class CursoEspecializacionDeleteView(CVRecordOwnerMixin, DeleteView):
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


class ExperienciaLaboralCreateView(CVPersonaAccessMixin, CreateView):
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
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            context = self.get_context_data(form=form)
            html = render_to_string('master/cv_experiencia_modal.html', context, request=self.request)
            return HttpResponse(html, status=400)

        return super().form_invalid(form)


class ExperienciaLaboralUpdateView(CVPersonaAccessMixin, UpdateView):
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
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            context = self.get_context_data(form=form)
            html = render_to_string('master/cv_experiencia_modal.html', context, request=self.request)
            return HttpResponse(html, status=400)

        return super().form_invalid(form)


class ExperienciaLaboralDeleteView(CVRecordOwnerMixin, DeleteView):
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
            experiencia_anios = request.POST.get('experiencia_anios') or 0
            nivel_educacion = request.POST.get('nivel_educacion', '')
            institucion_educacion = request.POST.get('institucion_educacion', '')

            if not convocatoria_id:
                return JsonResponse({'success': False, 'errors': {'convocatoria_id': ['Este campo es obligatorio']}})

            convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)

            if Postulacion.objects.filter(persona=persona, convocatoria=convocatoria).exists():
                msg = 'Esta persona ya está postulada a esta convocatoria.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': {'general': [msg]}}, status=400)
                messages.error(request, msg)
                return redirect('master:persona_detail', id=persona_id)

            try:
                experiencia_anios = int(experiencia_anios)
            except (TypeError, ValueError):
                experiencia_anios = 0

            Postulacion.objects.create(
                persona=persona,
                convocatoria=convocatoria,
                estado_postulacion=estado_postulacion or 'POSTULADO',
                observaciones=observaciones or None,
                experiencia_anios=max(experiencia_anios, 0),
                nivel_educacion=nivel_educacion or None,
                institucion_educacion=institucion_educacion or None,
            )

            acceso = AccesoCVPostulante.get_or_create_for_persona(persona)
            enlace_cv = request.build_absolute_uri(
                reverse('cv_publico:portal', kwargs={'token': acceso.token})
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Postulación creada correctamente',
                    'enlace_cv': enlace_cv,
                    'enlace_path': reverse('cv_publico:portal', kwargs={'token': acceso.token}),
                    'token': acceso.token,
                    'persona_id': persona.id,
                })

            messages.success(
                request,
                f'Postulación creada correctamente. Enlace CV: {enlace_cv}',
            )
            return redirect('master:persona_detail', id=persona_id)

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': {'general': [str(e)]}}, status=400)

            messages.error(request, f'Error al crear postulación: {str(e)}')
            return redirect('master:persona_detail', id=persona_id)

    return JsonResponse({'success': False, 'errors': {'method': ['Método no permitido']}}, status=405)


@login_required
def buscar_personas_disponibles(request):
    """Personas no postuladas a una convocatoria, para el modal de alta."""
    convocatoria_id = request.GET.get('convocatoria_id')
    q = (request.GET.get('q') or '').strip()
    if not convocatoria_id:
        return JsonResponse({'results': []})

    ya_postuladas = Postulacion.objects.filter(
        convocatoria_id=convocatoria_id
    ).values_list('persona_id', flat=True)

    qs = Persona.objects.exclude(id__in=ya_postuladas).order_by('apellido_paterno', 'nombres')
    if q:
        qs = qs.filter(
            Q(nombres__icontains=q) |
            Q(apellido_paterno__icontains=q) |
            Q(apellido_materno__icontains=q) |
            Q(numero_documento__icontains=q) |
            Q(email__icontains=q)
        )

    results = [
        {
            'id': p.id,
            'nombre': p.nombre_completo,
            'documento': f'{p.get_tipo_documento_display()}: {p.numero_documento}',
            'email': p.email or '',
        }
        for p in qs[:30]
    ]
    return JsonResponse({'results': results})


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

            acceso = AccesoCVPostulante.get_or_create_for_persona(persona)
            enlace_cv = request.build_absolute_uri(
                reverse('cv_publico:portal', kwargs={'token': acceso.token})
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True, 
                    'message': 'Registro completado exitosamente.',
                    'redirect_url': reverse('cv_publico:portal', kwargs={'token': acceso.token}),
                    'enlace_cv': enlace_cv,
                    'persona_id': persona.id,
                })
            
            from django.contrib import messages
            messages.success(request, 'Registro completado exitosamente.')
            return redirect('cv_publico:portal', token=acceso.token)
            
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
        cv, _ = CV.objects.get_or_create(persona=persona)
        formaciones = FormacionAcademica.objects.filter(cv=cv)
        cursos = CursoEspecializacion.objects.filter(cv=cv)
        experiencias = ExperienciaLaboral.objects.filter(cv=cv)

        context = {
            'persona': persona,
            'cv': cv,
            'formaciones': formaciones,
            'cursos': cursos,
            'experiencias': experiencias,
            'acceso_publico': bool(request.session.get('cv_postulante_persona_id') == persona.id),
        }
        return render(request, 'master/postulante_detail.html', context)
    except Persona.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Postulante no encontrado.')
        return redirect('master:registro_postulante')


def cv_token_wrap(view_func):
    """Adapta vistas de /postulante/<persona_id>/... para /cv/<token>/..."""
    from functools import wraps

    @wraps(view_func)
    def _wrapped(request, token, *args, **kwargs):
        acceso = AccesoCVPostulante.objects.filter(token=token).first()
        if not acceso or not acceso.vigente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method != 'GET':
                return JsonResponse(
                    {'success': False, 'errors': {'general': ['Enlace inválido o expirado.']}},
                    status=403,
                )
            return render(request, 'master/cv_acceso_invalido.html', {
                'motivo': 'Este enlace ha expirado o fue desactivado. Solicite uno nuevo a RRHH.',
            }, status=410)
        return view_func(request, acceso.persona_id, *args, **kwargs)

    return _wrapped


def cv_acceso_postulante(request, token):
    """Portal público: valida el hash y permite completar el CV sin login."""
    acceso = AccesoCVPostulante.objects.filter(token=token).first()
    if not acceso or not acceso.vigente:
        return render(request, 'master/cv_acceso_invalido.html', {
            'motivo': 'Este enlace ha expirado o fue desactivado. Solicite uno nuevo a RRHH.',
        }, status=410)

    acceso.ultimo_acceso = timezone.now()
    acceso.save(update_fields=['ultimo_acceso'])

    persona = acceso.persona
    cv, _ = CV.objects.get_or_create(persona=persona)
    context = {
        'persona': persona,
        'cv': cv,
        'formaciones': FormacionAcademica.objects.filter(cv=cv),
        'cursos': CursoEspecializacion.objects.filter(cv=cv),
        'experiencias': ExperienciaLaboral.objects.filter(cv=cv),
        'acceso_publico': True,
        'acceso_cv': acceso,
        'cv_api_base': f'/cv/{acceso.token}',
    }
    return render(request, 'master/postulante_detail.html', context)


def cv_acceso_legacy_redirect(request, token):
    """Compatibilidad: /master/cv-acceso/<token>/ → /cv/<token>/"""
    return redirect('cv_publico:portal', token=token)


def _build_enlace_cv(request, acceso):
    return request.build_absolute_uri(
        reverse('cv_publico:portal', kwargs={'token': acceso.token})
    )


@login_required
def generar_enlace_cv_postulante(request, persona_id):
    """Genera o renueva el enlace público de CV (hash) para una persona.
    El CV es independiente de cualquier convocatoria.
    """
    persona = get_object_or_404(Persona, pk=persona_id)

    renovar = request.GET.get('renovar') == '1' or request.POST.get('renovar') == '1'
    if renovar:
        try:
            acceso = persona.acceso_cv
            acceso.renovar()
        except AccesoCVPostulante.DoesNotExist:
            acceso = AccesoCVPostulante.get_or_create_for_persona(persona)
    else:
        acceso = AccesoCVPostulante.get_or_create_for_persona(persona)
        # Migrar tokens antiguos (urlsafe) a hash hex de 64 chars
        if len(acceso.token) != 64 or any(c not in '0123456789abcdef' for c in acceso.token):
            acceso.renovar()

    enlace = _build_enlace_cv(request, acceso)
    enlace_path = reverse('cv_publico:portal', kwargs={'token': acceso.token})
    return JsonResponse({
        'success': True,
        'enlace_cv': enlace,
        'enlace_path': enlace_path,
        'expira': acceso.fecha_expiracion.strftime('%d/%m/%Y %H:%M'),
        'token': acceso.token,
    })


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
            if 'archivo' in request.FILES:
                try:
                    formacion.archivo = validar_archivo_pdf(request.FILES['archivo'])
                    formacion.save(update_fields=['archivo'])
                except Exception as exc:
                    formacion.delete()
                    return JsonResponse({'success': False, 'errors': {'general': [str(exc)]}})
            
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
                    'archivo': formacion.archivo.url if formacion.archivo else '',
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
            if 'archivo' in request.FILES:
                formacion.archivo = validar_archivo_pdf(request.FILES['archivo'])
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
                    'archivo': formacion.archivo.url if formacion.archivo else '',
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
                try:
                    curso.certificado = validar_archivo_pdf(request.FILES['certificado'])
                    curso.save()
                except Exception as exc:
                    curso.delete()
                    from django.http import JsonResponse
                    return JsonResponse({'success': False, 'errors': {'general': [str(exc)]}})
            
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
                curso.certificado = validar_archivo_pdf(request.FILES['certificado'])
            
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
            if 'archivo' in request.FILES:
                try:
                    experiencia.archivo = validar_archivo_pdf(request.FILES['archivo'])
                    experiencia.save(update_fields=['archivo'])
                except Exception as exc:
                    experiencia.delete()
                    return JsonResponse({'success': False, 'errors': {'general': [str(exc)]}})
            
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
                    'archivo': experiencia.archivo.url if experiencia.archivo else '',
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
            if 'archivo' in request.FILES:
                experiencia.archivo = validar_archivo_pdf(request.FILES['archivo'])
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
                from .aprender_services import asignar_ruta_induccion
                n_cursos = len(asignar_ruta_induccion(colaborador))
                extra = f' Se asignaron {n_cursos} curso(s) de inducción.' if n_cursos else ''
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True, 
                        'message': (
                            f'Colaborador registrado exitosamente. '
                            f'Número de empleado: {colaborador.numero_empleado}.{extra}'
                        )
                    })
                
                messages.success(
                    request,
                    f'Colaborador registrado exitosamente. Número de empleado: {colaborador.numero_empleado}.{extra}',
                )
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


@admin_required
def usuarios_list(request):
    search = (request.GET.get('search') or '').strip()
    rol_filtro = (request.GET.get('rol') or '').strip()
    estado_filtro = (request.GET.get('estado') or '').strip()

    usuarios = User.objects.select_related('perfil_acceso', 'perfil').order_by('username')
    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(perfil__nombres__icontains=search)
            | Q(perfil__apellido_paterno__icontains=search)
            | Q(perfil__apellido_materno__icontains=search)
        )

    total = User.objects.count()
    activos = User.objects.filter(is_active=True).count()
    inactivos = total - activos
    administradores = PerfilAcceso.objects.filter(es_administrador=True).count()

    filas = []
    for u in usuarios:
        perfil = getattr(u, 'perfil_acceso', None)
        if perfil and perfil.es_administrador:
            rol = 'Administrador'
            modulos_txt = 'Todos los módulos'
            modulos_list = []
            es_admin = True
        elif perfil:
            rol = 'Usuario'
            modulos_list = modulos_labels(perfil.modulos)
            modulos_txt = ', '.join(modulos_list) or '—'
            es_admin = False
        else:
            rol = '—'
            modulos_txt = '—'
            modulos_list = []
            es_admin = False

        if rol_filtro == 'admin' and not es_admin:
            continue
        if rol_filtro == 'usuario' and (es_admin or rol == '—'):
            continue
        if estado_filtro == 'activo' and not u.is_active:
            continue
        if estado_filtro == 'inactivo' and u.is_active:
            continue

        persona = getattr(u, 'perfil', None)
        empleado_txt = persona.nombre_completo if persona else '—'
        filas.append({
            'user': u,
            'rol': rol,
            'es_admin': es_admin,
            'modulos_txt': modulos_txt,
            'modulos_list': modulos_list,
            'empleado_txt': empleado_txt,
            'activo': u.is_active,
        })

    return render(request, 'master/usuarios_list.html', {
        'filas': filas,
        'total': total,
        'activos': activos,
        'inactivos': inactivos,
        'administradores': administradores,
        'search': search,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
    })


@admin_required
def usuario_create(request):
    form = UsuarioAccesoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('master:usuarios_list')
    return render(request, 'master/usuario_form.html', {
        'form': form,
        'titulo': 'Nuevo usuario',
        'es_edicion': False,
    })


@admin_required
def usuario_edit(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    form = UsuarioAccesoForm(request.POST or None, user_instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('master:usuarios_list')
    return render(request, 'master/usuario_form.html', {
        'form': form,
        'titulo': f'Editar usuario: {usuario.username}',
        'es_edicion': True,
        'usuario_obj': usuario,
    })


@admin_required
def usuario_delete(request, user_id):
    usuario = get_object_or_404(User.objects.select_related('perfil_acceso', 'perfil'), pk=user_id)
    perfil = getattr(usuario, 'perfil_acceso', None)
    es_admin = bool(perfil and perfil.es_administrador)
    persona = getattr(usuario, 'perfil', None)

    if usuario.pk == request.user.pk:
        messages.error(request, 'No puede eliminar su propia cuenta.')
        return redirect('master:usuarios_list')

    if es_admin and PerfilAcceso.objects.filter(es_administrador=True).count() <= 1:
        messages.error(request, 'No puede eliminar al último administrador del sistema.')
        return redirect('master:usuarios_list')

    if request.method == 'POST':
        username = usuario.username
        # Evita borrar la Persona por CASCADE del OneToOne
        Persona.objects.filter(user=usuario).update(user=None)
        usuario.delete()
        messages.success(request, f'Usuario «{username}» eliminado correctamente.')
        return redirect('master:usuarios_list')

    return render(request, 'master/usuario_confirm_delete.html', {
        'usuario_obj': usuario,
        'es_admin': es_admin,
        'empleado_txt': persona.nombre_completo if persona else None,
    })


# ===== REGISTRO SEMANAL DE ACTIVIDADES =====

def deny_actividad_access_response(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'No autorizado'}, status=403)
    messages.error(request, 'No tiene permiso para acceder a este registro de actividades.')
    persona = get_user_persona(request.user)
    if persona:
        return redirect('master:mis_actividades')
    return redirect('master:ajustes')


class ActividadSemanalAccessMixin:
    """Restringe el acceso al propio empleado vinculado (o admin)."""

    def _persona_puede_acceder_registro(self, user, registro):
        if user_is_admin(user):
            return True
        persona = get_user_persona(user)
        return persona is not None and registro.persona_id == persona.pk

    def _persona_puede_acceder_actividad(self, user, actividad):
        return self._persona_puede_acceder_registro(user, actividad.registro)


@login_required
def mis_actividades_view(request):
    """Pantalla principal de registro semanal de actividades."""
    persona = get_user_persona(request.user)
    if persona is None:
        messages.info(
            request,
            'Su cuenta no está vinculada a un empleado. Contacte al administrador.',
        )
        return redirect('master:ajustes')

    iso = date.today().isocalendar()
    anio = int(request.GET.get('anio', iso[0]))
    semana = int(request.GET.get('semana', iso[1]))

    registro = get_or_create_registro_semana(persona, anio, semana)
    actividades = registro.actividades.all().order_by('fecha', 'id')

    anio_anterior, semana_anterior = semana_iso_desplazada(anio, semana, -1)
    anio_siguiente, semana_siguiente = semana_iso_desplazada(anio, semana, 1)

    tipos_por_grupo = {
        grupo: [{'value': clave, 'label': label} for clave, label in tipos]
        for grupo, tipos in TIPOS_POR_GRUPO.items()
    }

    return render(request, 'master/mis_actividades.html', {
        'persona': persona,
        'registro': registro,
        'actividades': actividades,
        'anio': anio,
        'semana': semana,
        'fecha_inicio': registro.fecha_inicio,
        'fecha_fin': registro.fecha_fin,
        'anio_anterior': anio_anterior,
        'semana_anterior': semana_anterior,
        'anio_siguiente': anio_siguiente,
        'semana_siguiente': semana_siguiente,
        'total_actividades': actividades.count(),
        'tipos_por_grupo_json': json.dumps(tipos_por_grupo),
        'grupo_choices': GRUPO_CHOICES,
    })


@login_required
def mis_actividades_pdf_view(request):
    """Descarga PDF del registro semanal de actividades."""
    persona = get_user_persona(request.user)
    if persona is None:
        messages.info(
            request,
            'Su cuenta no está vinculada a un empleado. Contacte al administrador.',
        )
        return redirect('master:ajustes')

    iso = date.today().isocalendar()
    anio = int(request.GET.get('anio', iso[0]))
    semana = int(request.GET.get('semana', iso[1]))

    registro = get_or_create_registro_semana(persona, anio, semana)
    actividades = list(registro.actividades.all().order_by('fecha', 'id'))

    pdf_bytes = generar_actividades_semanales_pdf(persona, registro, actividades)
    filename = f'actividades_semana_{semana}_{anio}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


class ActividadSemanalCreateView(ActividadSemanalAccessMixin, CreateView):
    """Alta de actividad semanal vía modal AJAX."""
    model = ActividadSemanal
    form_class = ActividadSemanalForm
    template_name = 'master/actividad_semanal_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not user_can_manage_own_actividades(request.user):
            return deny_actividad_access_response(request)
        persona = get_user_persona(request.user)
        if persona is None:
            return deny_actividad_access_response(request)
        self.registro = get_or_create_registro_semana(
            persona,
            kwargs['anio'],
            kwargs['semana'],
        )
        if not self._persona_puede_acceder_registro(request.user, self.registro):
            return deny_actividad_access_response(request)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['registro'] = self.registro
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_edicion'] = False
        context['anio'] = self.kwargs['anio']
        context['semana'] = self.kwargs['semana']
        return context

    def get_template_names(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/includes/actividad_semanal_modal.html']
        return [self.template_name]

    def form_valid(self, form):
        form.instance.registro = self.registro
        form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Actividad registrada correctamente'})
        return redirect(f"{reverse('master:mis_actividades')}?anio={self.kwargs['anio']}&semana={self.kwargs['semana']}")

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)


class ActividadSemanalUpdateView(ActividadSemanalAccessMixin, UpdateView):
    """Edición de actividad semanal vía modal AJAX."""
    model = ActividadSemanal
    form_class = ActividadSemanalForm
    template_name = 'master/actividad_semanal_form.html'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        if not user_can_manage_own_actividades(request.user):
            return deny_actividad_access_response(request)
        actividad = get_object_or_404(ActividadSemanal, pk=kwargs['pk'])
        if not self._persona_puede_acceder_actividad(request.user, actividad):
            return deny_actividad_access_response(request)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['registro'] = self.object.registro
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_edicion'] = True
        context['anio'] = self.object.registro.anio
        context['semana'] = self.object.registro.semana
        return context

    def get_template_names(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ['master/includes/actividad_semanal_modal.html']
        return [self.template_name]

    def form_valid(self, form):
        form.save()
        registro = form.instance.registro
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Actividad actualizada correctamente'})
        return redirect(f"{reverse('master:mis_actividades')}?anio={registro.anio}&semana={registro.semana}")

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)


class ActividadSemanalDeleteView(ActividadSemanalAccessMixin, DeleteView):
    """Eliminación de actividad semanal vía modal AJAX."""
    model = ActividadSemanal
    pk_url_kwarg = 'pk'
    template_name = 'master/actividad_semanal_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not user_can_manage_own_actividades(request.user):
            return deny_actividad_access_response(request)
        actividad = get_object_or_404(ActividadSemanal, pk=kwargs['pk'])
        if not self._persona_puede_acceder_actividad(request.user, actividad):
            return deny_actividad_access_response(request)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            html = render_to_string(
                self.template_name,
                {'object': self.get_object()},
                request=request,
            )
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        actividad = self.get_object()
        anio = actividad.registro.anio
        semana = actividad.registro.semana
        actividad.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Actividad eliminada correctamente'})
        return redirect(f"{reverse('master:mis_actividades')}?anio={anio}&semana={semana}")
