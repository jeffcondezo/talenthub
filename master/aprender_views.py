"""Vistas del módulo Aprender (inducción + capacitaciones)."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .aprender_services import (
    asignar_ruta_induccion,
    cursos_capacitacion_visibles,
    induccion_items_para_colaborador,
    marcar_en_curso_si_pendiente,
)
from .forms import (
    CalificarAsignacionForm,
    CursoAprendizajeForm,
    RutaInduccionCursoForm,
    RutaInduccionForm,
)
from .models import (
    Area,
    AsignacionCurso,
    Cargo,
    Colaborador,
    CursoAprendizaje,
    RutaInduccion,
    RutaInduccionCurso,
)
from .permissions import get_user_persona, user_has_module, user_is_admin


def _hr_aprender(user):
    return user_is_admin(user) or user_has_module(user, 'capacitacion')


def hr_aprender_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _hr_aprender(request.user):
            messages.error(request, 'No tiene permiso para administrar Aprender.')
            return redirect('master:inicio')
        return view_func(request, *args, **kwargs)
    return _wrapped


def _colaborador_de_user(user):
    persona = get_user_persona(user)
    if not persona:
        return None
    return Colaborador.objects.filter(persona=persona).select_related('cargo', 'cargo__area').first()


def empleado_aprender_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if _hr_aprender(request.user) or _colaborador_de_user(request.user):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Debe estar vinculado como empleado para ver esta sección.')
        return redirect('master:ajustes')
    return _wrapped


def _list_url(tipo):
    return 'master:aprender_induccion_cursos' if tipo == 'INDUCCION' else 'master:aprender_cap_cursos'


def _seguimiento_url(origen):
    return (
        'master:aprender_induccion_seguimiento'
        if origen == 'INDUCCION'
        else 'master:aprender_cap_seguimiento'
    )


# ---------- Hubs admin ----------

@login_required
def aprender_hub(request):
    if _hr_aprender(request.user):
        return redirect('master:aprender_induccion')
    if _colaborador_de_user(request.user):
        return redirect('master:aprender_mi_induccion')
    messages.info(request, 'El módulo Aprender estará disponible con perfil de empleado o permiso de capacitación.')
    return redirect('master:ajustes')


@hr_aprender_required
def induccion_hub(request):
    return redirect('master:aprender_induccion_cursos')


@hr_aprender_required
def capacitacion_hub(request):
    return redirect('master:aprender_cap_cursos')


# ---------- Catálogo HR (por tipo) ----------

@hr_aprender_required
def curso_list(request, tipo='INDUCCION'):
    if tipo not in ('INDUCCION', 'CAPACITACION'):
        tipo = 'INDUCCION'
    qs = CursoAprendizaje.objects.filter(tipo=tipo).annotate(
        n_asignaciones=Count('asignaciones'),
    )
    search = (request.GET.get('search') or '').strip()
    activo = (request.GET.get('activo') or '').strip()
    if search:
        qs = qs.filter(Q(nombre__icontains=search) | Q(descripcion__icontains=search))
    if activo == '1':
        qs = qs.filter(activo=True)
    elif activo == '0':
        qs = qs.filter(activo=False)
    return render(request, 'master/aprender_cursos.html', {
        'cursos': qs,
        'search': search,
        'activo': activo,
        'tipo_fijo': tipo,
        'seccion': 'induccion' if tipo == 'INDUCCION' else 'capacitacion',
        'titulo': 'Cursos de inducción' if tipo == 'INDUCCION' else 'Cursos de capacitación',
        'subtitulo': (
            'Catálogo exclusivo para rutas de inducción.'
            if tipo == 'INDUCCION'
            else 'Catálogo de cursos libres para empleados.'
        ),
        'create_url': reverse(
            'master:aprender_induccion_curso_create'
            if tipo == 'INDUCCION'
            else 'master:aprender_cap_curso_create'
        ),
        'total': CursoAprendizaje.objects.filter(tipo=tipo).count(),
        'activos': CursoAprendizaje.objects.filter(tipo=tipo, activo=True).count(),
    })


@hr_aprender_required
def curso_create(request, tipo='INDUCCION'):
    if tipo not in ('INDUCCION', 'CAPACITACION'):
        tipo = 'INDUCCION'
    form = CursoAprendizajeForm(request.POST or None, tipo_fijo=tipo)
    if request.method == 'POST' and form.is_valid():
        form.save(user=request.user)
        messages.success(request, 'Curso creado correctamente.')
        return redirect(_list_url(tipo))
    return render(request, 'master/aprender_curso_form.html', {
        'form': form,
        'titulo': 'Nuevo curso de inducción' if tipo == 'INDUCCION' else 'Nuevo curso de capacitación',
        'es_edicion': False,
        'tipo_fijo': tipo,
        'seccion': 'induccion' if tipo == 'INDUCCION' else 'capacitacion',
        'list_url': reverse(_list_url(tipo)),
        'mostrar_alcance': tipo == 'CAPACITACION',
    })


@hr_aprender_required
def curso_edit(request, pk):
    curso = get_object_or_404(CursoAprendizaje, pk=pk)
    tipo = curso.tipo if curso.tipo in ('INDUCCION', 'CAPACITACION') else 'INDUCCION'
    form = CursoAprendizajeForm(request.POST or None, instance=curso, tipo_fijo=tipo)
    if request.method == 'POST' and form.is_valid():
        form.save(user=request.user)
        messages.success(request, 'Curso actualizado.')
        return redirect(_list_url(tipo))
    return render(request, 'master/aprender_curso_form.html', {
        'form': form,
        'titulo': f'Editar: {curso.nombre}',
        'es_edicion': True,
        'curso': curso,
        'tipo_fijo': tipo,
        'seccion': 'induccion' if tipo == 'INDUCCION' else 'capacitacion',
        'list_url': reverse(_list_url(tipo)),
        'mostrar_alcance': tipo == 'CAPACITACION',
    })


@hr_aprender_required
def curso_delete(request, pk):
    curso = get_object_or_404(CursoAprendizaje, pk=pk)
    tipo = curso.tipo if curso.tipo in ('INDUCCION', 'CAPACITACION') else 'INDUCCION'
    if request.method == 'POST':
        nombre = curso.nombre
        curso.delete()
        messages.success(request, f'Curso «{nombre}» eliminado.')
        return redirect(_list_url(tipo))
    return render(request, 'master/aprender_confirm_delete.html', {
        'titulo': 'Eliminar curso',
        'mensaje': f'¿Eliminar el curso «{curso.nombre}»? También se eliminarán asignaciones y vínculos en rutas.',
        'cancel_url': reverse(_list_url(tipo)),
        'seccion': 'induccion' if tipo == 'INDUCCION' else 'capacitacion',
    })


# ---------- Rutas HR (solo inducción) ----------

@hr_aprender_required
def ruta_list(request):
    qs = RutaInduccion.objects.select_related('cargo', 'cargo__area').annotate(
        n_cursos=Count('items'),
    )
    area = (request.GET.get('area') or '').strip()
    cargo = (request.GET.get('cargo') or '').strip()
    if area:
        qs = qs.filter(cargo__area_id=area)
    if cargo:
        qs = qs.filter(cargo_id=cargo)
    return render(request, 'master/aprender_rutas.html', {
        'rutas': qs,
        'areas': Area.objects.filter(activo=True).order_by('nombre'),
        'cargos': Cargo.objects.filter(activo=True).select_related('area').order_by('nombre'),
        'area': area,
        'cargo': cargo,
        'total': RutaInduccion.objects.count(),
        'activas': RutaInduccion.objects.filter(activo=True).count(),
        'seccion': 'induccion',
    })


@hr_aprender_required
def ruta_create(request):
    form = RutaInduccionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ruta = form.save()
        messages.success(request, 'Ruta creada. Ahora agregue los cursos en secuencia.')
        return redirect('master:aprender_ruta_detail', pk=ruta.pk)
    return render(request, 'master/aprender_ruta_form.html', {
        'form': form,
        'titulo': 'Nueva ruta de inducción',
        'seccion': 'induccion',
    })


@hr_aprender_required
def ruta_detail(request, pk):
    ruta = get_object_or_404(
        RutaInduccion.objects.select_related('cargo', 'cargo__area'),
        pk=pk,
    )
    items = ruta.items.select_related('curso', 'prerequisito').order_by('orden', 'id')
    item_form = RutaInduccionCursoForm(ruta=ruta)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'add_item':
            item_form = RutaInduccionCursoForm(request.POST, ruta=ruta)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.ruta = ruta
                item.save()
                messages.success(request, 'Curso agregado a la ruta.')
                return redirect('master:aprender_ruta_detail', pk=ruta.pk)
        elif accion == 'toggle':
            ruta.activo = not ruta.activo
            ruta.save(update_fields=['activo', 'fecha_actualizacion'])
            messages.success(request, 'Estado de la ruta actualizado.')
            return redirect('master:aprender_ruta_detail', pk=ruta.pk)
        elif accion == 'reasignar':
            cols = Colaborador.objects.filter(cargo=ruta.cargo, estado_laboral='ACTIVO')
            total = 0
            for c in cols:
                total += len(asignar_ruta_induccion(c))
            messages.success(request, f'Reasignación: {total} curso(s) nuevos para empleados del cargo.')
            return redirect('master:aprender_ruta_detail', pk=ruta.pk)
    return render(request, 'master/aprender_ruta_detail.html', {
        'ruta': ruta,
        'items': items,
        'item_form': item_form,
        'seccion': 'induccion',
    })


@hr_aprender_required
def ruta_item_delete(request, pk, item_id):
    ruta = get_object_or_404(RutaInduccion, pk=pk)
    item = get_object_or_404(RutaInduccionCurso, pk=item_id, ruta=ruta)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Curso quitado de la ruta.')
    return redirect('master:aprender_ruta_detail', pk=ruta.pk)


@hr_aprender_required
def ruta_delete(request, pk):
    ruta = get_object_or_404(RutaInduccion, pk=pk)
    if request.method == 'POST':
        nombre = str(ruta)
        ruta.delete()
        messages.success(request, f'{nombre} eliminada.')
        return redirect('master:aprender_rutas')
    return render(request, 'master/aprender_confirm_delete.html', {
        'titulo': 'Eliminar ruta',
        'mensaje': f'¿Eliminar la ruta de «{ruta.cargo.nombre}»? Las asignaciones de empleados no se borran.',
        'cancel_url': reverse('master:aprender_ruta_detail', kwargs={'pk': pk}),
        'seccion': 'induccion',
    })


# ---------- Seguimiento / calificar ----------

@hr_aprender_required
def seguimiento_list(request, origen='INDUCCION'):
    if origen not in ('INDUCCION', 'CAPACITACION'):
        origen = 'INDUCCION'
    qs = AsignacionCurso.objects.filter(origen=origen).select_related(
        'colaborador__persona', 'colaborador__cargo', 'curso', 'evaluado_por',
    )
    estado = (request.GET.get('estado') or '').strip()
    cargo = (request.GET.get('cargo') or '').strip()
    search = (request.GET.get('search') or '').strip()
    if estado:
        qs = qs.filter(estado=estado)
    if cargo:
        qs = qs.filter(colaborador__cargo_id=cargo)
    if search:
        qs = qs.filter(
            Q(colaborador__persona__nombres__icontains=search)
            | Q(colaborador__persona__apellido_paterno__icontains=search)
            | Q(curso__nombre__icontains=search)
        )
    return render(request, 'master/aprender_seguimiento.html', {
        'asignaciones': qs[:200],
        'origen_fijo': origen,
        'estado': estado,
        'cargo': cargo,
        'search': search,
        'cargos': Cargo.objects.filter(activo=True).order_by('nombre'),
        'estado_choices': AsignacionCurso.ESTADO_CHOICES,
        'titulo': 'Seguimiento de inducción' if origen == 'INDUCCION' else 'Seguimiento de capacitaciones',
        'seccion': 'induccion' if origen == 'INDUCCION' else 'capacitacion',
        'total': AsignacionCurso.objects.filter(origen=origen).count(),
        'pendientes': AsignacionCurso.objects.filter(
            origen=origen, estado__in=['PENDIENTE', 'EN_CURSO', 'DESAPROBADO']
        ).count(),
        'aprobados': AsignacionCurso.objects.filter(origen=origen, estado='APROBADO').count(),
    })


@hr_aprender_required
def calificar_asignacion(request, pk):
    asignacion = get_object_or_404(
        AsignacionCurso.objects.select_related(
            'curso', 'colaborador__persona', 'colaborador__cargo',
        ),
        pk=pk,
    )
    form = CalificarAsignacionForm(
        request.POST or None,
        initial={
            'nota': asignacion.nota,
            'comentario_evaluador': asignacion.comentario_evaluador or '',
        },
    )
    if request.method == 'POST' and form.is_valid():
        asignacion.aplicar_nota(
            form.cleaned_data['nota'],
            user=request.user,
            comentario=form.cleaned_data.get('comentario_evaluador') or '',
        )
        messages.success(
            request,
            f'Nota registrada. Estado: {asignacion.get_estado_display()}.',
        )
        return redirect(_seguimiento_url(asignacion.origen))
    return render(request, 'master/aprender_calificar.html', {
        'asignacion': asignacion,
        'form': form,
        'seccion': 'induccion' if asignacion.origen == 'INDUCCION' else 'capacitacion',
        'volver_url': reverse(_seguimiento_url(asignacion.origen)),
    })


# ---------- Empleado ----------

@empleado_aprender_required
def mi_induccion(request):
    colaborador = _colaborador_de_user(request.user)
    if not colaborador and _hr_aprender(request.user):
        return render(request, 'master/aprender_mi_induccion.html', {
            'items': [],
            'colaborador': None,
            'es_hr_sin_ficha': True,
            'seccion': 'empleado',
        })
    asignar_ruta_induccion(colaborador)
    items = induccion_items_para_colaborador(colaborador)
    aprobados = sum(1 for i in items if i['estado'] == 'APROBADO')
    return render(request, 'master/aprender_mi_induccion.html', {
        'items': items,
        'colaborador': colaborador,
        'aprobados': aprobados,
        'total': len(items),
        'es_hr_sin_ficha': False,
        'seccion': 'empleado',
    })


@empleado_aprender_required
def mi_curso_detail(request, asignacion_id):
    colaborador = _colaborador_de_user(request.user)
    asignacion = get_object_or_404(
        AsignacionCurso.objects.select_related('curso', 'colaborador'),
        pk=asignacion_id,
    )
    if not _hr_aprender(request.user):
        if not colaborador or asignacion.colaborador_id != colaborador.id:
            return HttpResponseForbidden('No autorizado')
        if asignacion.origen == 'INDUCCION':
            items = induccion_items_para_colaborador(colaborador)
            match = next(
                (i for i in items if i['asignacion'] and i['asignacion'].id == asignacion.id),
                None,
            )
            if match and not match['desbloqueado']:
                messages.warning(request, 'Este curso está bloqueado hasta aprobar el requisito.')
                return redirect('master:aprender_mi_induccion')
        marcar_en_curso_si_pendiente(asignacion)
    return render(request, 'master/aprender_curso_detalle.html', {
        'asignacion': asignacion,
        'curso': asignacion.curso,
        'modo_empleado': True,
        'seccion': 'empleado',
    })


@empleado_aprender_required
def mis_capacitaciones(request):
    colaborador = _colaborador_de_user(request.user)
    if not colaborador:
        return render(request, 'master/aprender_mis_capacitaciones.html', {
            'cards': [],
            'colaborador': None,
            'es_hr_sin_ficha': True,
            'seccion': 'empleado',
        })
    cursos = list(cursos_capacitacion_visibles(colaborador))
    inscritos = {
        a.curso_id: a
        for a in AsignacionCurso.objects.filter(
            colaborador=colaborador,
            origen='CAPACITACION',
        )
    }
    cards = [{'curso': c, 'asignacion': inscritos.get(c.id)} for c in cursos]
    return render(request, 'master/aprender_mis_capacitaciones.html', {
        'cards': cards,
        'colaborador': colaborador,
        'es_hr_sin_ficha': False,
        'seccion': 'empleado',
    })


@empleado_aprender_required
def inscribir_capacitacion(request, curso_id):
    colaborador = _colaborador_de_user(request.user)
    if not colaborador:
        messages.error(request, 'Solo empleados pueden inscribirse.')
        return redirect('master:aprender_capacitaciones')
    curso = get_object_or_404(CursoAprendizaje, pk=curso_id, activo=True, tipo='CAPACITACION')
    if not curso.visible_para_cargo(colaborador.cargo):
        messages.error(request, 'Este curso no está disponible para su cargo.')
        return redirect('master:aprender_capacitaciones')
    if request.method == 'POST':
        asig, created = AsignacionCurso.objects.get_or_create(
            colaborador=colaborador,
            curso=curso,
            origen='CAPACITACION',
            defaults={'estado': 'PENDIENTE'},
        )
        if created:
            messages.success(request, f'Inscripción a «{curso.nombre}» realizada.')
        else:
            messages.info(request, 'Ya estaba inscrito en este curso.')
        return redirect('master:aprender_mi_curso', asignacion_id=asig.id)
    return redirect('master:aprender_capacitaciones')
