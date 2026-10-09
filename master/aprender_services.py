"""Helpers del módulo Aprender: asignación de rutas y reglas de desbloqueo."""
from __future__ import annotations

from django.db.models import Prefetch, Q

from .models import (
    AsignacionCurso,
    Colaborador,
    CursoAprendizaje,
    RutaInduccion,
    RutaInduccionCurso,
)


def asignar_ruta_induccion(colaborador: Colaborador) -> list[AsignacionCurso]:
    """
    Crea asignaciones PENDIENTE por cada curso de la ruta activa del cargo.
    No duplica si ya existe asignación de inducción para ese curso.
    """
    if not colaborador or not colaborador.cargo_id:
        return []

    try:
        ruta = RutaInduccion.objects.prefetch_related('items').get(
            cargo_id=colaborador.cargo_id,
            activo=True,
        )
    except RutaInduccion.DoesNotExist:
        return []

    creadas = []
    for item in ruta.items.select_related('curso').order_by('orden', 'id'):
        if not item.curso_id or not item.curso.activo:
            continue
        asignacion, created = AsignacionCurso.objects.get_or_create(
            colaborador=colaborador,
            curso=item.curso,
            origen='INDUCCION',
            defaults={'estado': 'PENDIENTE'},
        )
        if created:
            creadas.append(asignacion)
    return creadas


def cursos_capacitacion_visibles(colaborador: Colaborador | None):
    """QuerySet de cursos de capacitación disponibles para el colaborador."""
    qs = CursoAprendizaje.objects.filter(
        activo=True,
        tipo='CAPACITACION',
    )
    if not colaborador or not colaborador.cargo_id:
        return qs.filter(alcance='TODOS')
    return qs.filter(
        Q(alcance='TODOS') | Q(alcance='POR_CARGO', cargos_visibles=colaborador.cargo_id)
    ).distinct()


def induccion_items_para_colaborador(colaborador: Colaborador):
    """
    Devuelve lista de dicts con item de ruta, asignación y si está desbloqueado.
    """
    if not colaborador or not colaborador.cargo_id:
        return []

    try:
        ruta = RutaInduccion.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=RutaInduccionCurso.objects.select_related(
                    'curso', 'prerequisito'
                ).order_by('orden', 'id'),
            )
        ).get(cargo_id=colaborador.cargo_id, activo=True)
    except RutaInduccion.DoesNotExist:
        return []

    asignaciones = {
        a.curso_id: a
        for a in AsignacionCurso.objects.filter(
            colaborador=colaborador,
            origen='INDUCCION',
        ).select_related('curso')
    }
    aprobados = {
        cid for cid, a in asignaciones.items() if a.estado == 'APROBADO'
    }

    resultado = []
    for item in ruta.items.all():
        asig = asignaciones.get(item.curso_id)
        if item.prerequisito_id:
            desbloqueado = item.prerequisito_id in aprobados
        else:
            desbloqueado = True
        resultado.append({
            'item': item,
            'curso': item.curso,
            'asignacion': asig,
            'desbloqueado': desbloqueado,
            'estado': asig.estado if asig else 'SIN_ASIGNAR',
        })
    return resultado


def marcar_en_curso_si_pendiente(asignacion: AsignacionCurso) -> AsignacionCurso:
    if asignacion.estado == 'PENDIENTE':
        asignacion.estado = 'EN_CURSO'
        asignacion.save(update_fields=['estado', 'fecha_actualizacion'])
    return asignacion
