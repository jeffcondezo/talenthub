from django.urls import path
from . import views
from . import aprender_views
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView # <--- Importante


app_name = 'master'

urlpatterns = [
    
    path('', RedirectView.as_view(url='/master/login/', permanent=True)),
    # Página de login
    path('login/', views.CustomLoginView.as_view(), name='login'),

    path('inicio/', views.inicio_view, name='inicio'),
    path('ajustes/', views.ajustes_view, name='ajustes'),
    path('mi-perfil/', views.mi_perfil_view, name='mi_perfil'),
    path('mis-actividades/', views.mis_actividades_view, name='mis_actividades'),
    path('mis-actividades/pdf/', views.mis_actividades_pdf_view, name='mis_actividades_pdf'),
    path(
        'mis-actividades/<int:anio>/<int:semana>/actividad/',
        views.ActividadSemanalCreateView.as_view(),
        name='actividad_semanal_create',
    ),
    path(
        'mis-actividades/actividad/<int:pk>/',
        views.ActividadSemanalUpdateView.as_view(),
        name='actividad_semanal_edit',
    ),
    path(
        'mis-actividades/actividad/<int:pk>/eliminar/',
        views.ActividadSemanalDeleteView.as_view(),
        name='actividad_semanal_delete',
    ),
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:user_id>/editar/', views.usuario_edit, name='usuario_edit'),
    path('usuarios/<int:user_id>/eliminar/', views.usuario_delete, name='usuario_delete'),
    
    # Página de logout
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Compatibilidad antiguas
    path('induccion/', RedirectView.as_view(pattern_name='master:aprender_mi_induccion', permanent=False), name='induccion'),
    path('capacitacion/', RedirectView.as_view(pattern_name='master:aprender_capacitaciones', permanent=False), name='capacitacion'),

    # Aprender — hubs
    path('aprender/', aprender_views.aprender_hub, name='aprender'),
    path('aprender/induccion/', aprender_views.induccion_hub, name='aprender_induccion'),
    path('aprender/capacitacion/', aprender_views.capacitacion_hub, name='aprender_capacitacion'),

    # Admin inducción
    path(
        'aprender/induccion/cursos/',
        aprender_views.curso_list,
        {'tipo': 'INDUCCION'},
        name='aprender_induccion_cursos',
    ),
    path(
        'aprender/induccion/cursos/nuevo/',
        aprender_views.curso_create,
        {'tipo': 'INDUCCION'},
        name='aprender_induccion_curso_create',
    ),
    path('aprender/induccion/rutas/', aprender_views.ruta_list, name='aprender_rutas'),
    path('aprender/induccion/rutas/nueva/', aprender_views.ruta_create, name='aprender_ruta_create'),
    path('aprender/induccion/rutas/<int:pk>/', aprender_views.ruta_detail, name='aprender_ruta_detail'),
    path('aprender/induccion/rutas/<int:pk>/eliminar/', aprender_views.ruta_delete, name='aprender_ruta_delete'),
    path(
        'aprender/induccion/rutas/<int:pk>/item/<int:item_id>/eliminar/',
        aprender_views.ruta_item_delete,
        name='aprender_ruta_item_delete',
    ),
    path(
        'aprender/induccion/seguimiento/',
        aprender_views.seguimiento_list,
        {'origen': 'INDUCCION'},
        name='aprender_induccion_seguimiento',
    ),

    # Admin capacitaciones
    path(
        'aprender/capacitacion/cursos/',
        aprender_views.curso_list,
        {'tipo': 'CAPACITACION'},
        name='aprender_cap_cursos',
    ),
    path(
        'aprender/capacitacion/cursos/nuevo/',
        aprender_views.curso_create,
        {'tipo': 'CAPACITACION'},
        name='aprender_cap_curso_create',
    ),
    path(
        'aprender/capacitacion/seguimiento/',
        aprender_views.seguimiento_list,
        {'origen': 'CAPACITACION'},
        name='aprender_cap_seguimiento',
    ),

    # CRUD compartido de curso / calificación
    path('aprender/cursos/<int:pk>/editar/', aprender_views.curso_edit, name='aprender_curso_edit'),
    path('aprender/cursos/<int:pk>/eliminar/', aprender_views.curso_delete, name='aprender_curso_delete'),
    path('aprender/seguimiento/<int:pk>/calificar/', aprender_views.calificar_asignacion, name='aprender_calificar'),

    # Redirects de URLs antiguas unificadas
    path('aprender/cursos/', RedirectView.as_view(pattern_name='master:aprender_induccion_cursos', permanent=False), name='aprender_cursos'),
    path('aprender/cursos/nuevo/', RedirectView.as_view(pattern_name='master:aprender_induccion_curso_create', permanent=False), name='aprender_curso_create'),
    path('aprender/rutas/', RedirectView.as_view(pattern_name='master:aprender_rutas', permanent=False)),
    path('aprender/seguimiento/', RedirectView.as_view(pattern_name='master:aprender_induccion_seguimiento', permanent=False), name='aprender_seguimiento'),

    # Empleado (Cuenta)
    path('aprender/mi-induccion/', aprender_views.mi_induccion, name='aprender_mi_induccion'),
    path('aprender/mi-curso/<int:asignacion_id>/', aprender_views.mi_curso_detail, name='aprender_mi_curso'),
    path('aprender/capacitaciones/', aprender_views.mis_capacitaciones, name='aprender_capacitaciones'),
    path(
        'aprender/inscribir/<int:curso_id>/',
        aprender_views.inscribir_capacitacion,
        name='aprender_inscribir',
    ),

    # Proyectos
    path('proyecto/', views.proyecto_view, name='proyecto'),
    path('proyecto/nuevo/', views.proyecto_create, name='proyecto_create'),
    path('proyecto/sugerir-recursos/', views.proyecto_sugerir_recursos, name='proyecto_sugerir'),
    path('proyecto/<int:pk>/', views.proyecto_detail, name='proyecto_detail'),
    path('proyecto/<int:pk>/editar/', views.proyecto_edit, name='proyecto_edit'),
    path('proyecto/<int:pk>/eliminar/', views.proyecto_delete, name='proyecto_delete'),
    path('proyecto/<int:pk>/asignar/', views.proyecto_asignar, name='proyecto_asignar'),
    path(
        'proyecto/<int:pk>/asignacion/<int:asignacion_id>/editar/',
        views.proyecto_asignacion_edit,
        name='proyecto_asignacion_edit',
    ),
    path(
        'proyecto/<int:pk>/asignacion/<int:asignacion_id>/quitar/',
        views.proyecto_asignacion_quitar,
        name='proyecto_asignacion_quitar',
    ),
    path('perfiles/', views.perfiles_view, name='perfiles'),
    path('analitica/', views.analitica_view, name='analitica'),
    path('cv/', views.cv_view, name='cv'),
    path('cv/<int:id>/', views.CVDetailView.as_view(), name='cv_detail'),
    
    # URLs para gestión de CV
    path('cv/<int:persona_id>/formacion/', views.FormacionAcademicaCreateView.as_view(), name='cv_formacion_create'),
    path('cv/<int:persona_id>/formacion/<int:formacion_id>/', views.FormacionAcademicaUpdateView.as_view(), name='cv_formacion_edit'),
    path('cv/formacion/<int:formacion_id>/delete/', views.FormacionAcademicaDeleteView.as_view(), name='cv_formacion_delete'),
    
    path('cv/<int:persona_id>/curso/', views.CursoEspecializacionCreateView.as_view(), name='cv_curso_create'),
    path('cv/<int:persona_id>/curso/<int:curso_id>/', views.CursoEspecializacionUpdateView.as_view(), name='cv_curso_edit'),
    path('cv/curso/<int:curso_id>/delete/', views.CursoEspecializacionDeleteView.as_view(), name='cv_curso_delete'),
    
    path('cv/<int:persona_id>/experiencia/', views.ExperienciaLaboralCreateView.as_view(), name='cv_experiencia_create'),
    path('cv/<int:persona_id>/experiencia/<int:experiencia_id>/', views.ExperienciaLaboralUpdateView.as_view(), name='cv_experiencia_edit'),
    path('cv/experiencia/<int:experiencia_id>/delete/', views.ExperienciaLaboralDeleteView.as_view(), name='cv_experiencia_delete'),
    path('personas/', views.PersonasListView.as_view(), name='personas'),
    path('personas/create/', views.PersonaCreateView.as_view(), name='persona_create'),
    path('personas/<int:id>/', views.PersonaDetailView.as_view(), name='persona_detail'),
    path('personas/<int:id>/edit/', views.PersonaUpdateView.as_view(), name='persona_edit'),
    path('personas/<int:id>/cv/edit/', views.cv_perfil_edit, name='persona_cv_edit'),
    path('personas/<int:id>/skills/', views.persona_skills_update, name='persona_skills_update'),
    path('personas/<int:id>/empleo/edit/', views.colaborador_empleo_edit, name='persona_empleo_edit'),
    path('personas/<int:id>/delete/', views.PersonaDeleteView.as_view(), name='persona_delete'),
    path('convocatorias/<int:convocatoria_id>/postulantes/', views.PostulantesListView.as_view(), name='postulantes'),
    path(
        'convocatorias/<int:convocatoria_id>/comparar/',
        views.comparar_postulantes,
        name='comparar_postulantes',
    ),
    path('convocatorias/', views.ConvocatoriasListView.as_view(), name='convocatorias'),
    path('convocatorias/create/', views.ConvocatoriaCreateView.as_view(), name='convocatoria_create'),
    path('convocatorias/<int:id>/', views.ConvocatoriaDetailView.as_view(), name='convocatoria_detail'),
    path('convocatorias/<int:id>/edit/', views.ConvocatoriaUpdateView.as_view(), name='convocatoria_edit'),
    path('convocatorias/<int:id>/delete/', views.ConvocatoriaDeleteView.as_view(), name='convocatoria_delete'),
    path('colaboradores/', views.colaboradores_view, name='colaboradores'),
    path('colaboradores/<int:id>/delete/', views.eliminar_colaborador, name='eliminar_colaborador'),
    
    # URLs AJAX para filtrado en cascada de ubicaciones
    path('ajax/get-provincias/', views.get_provincias, name='get_provincias'),
    path('ajax/get-distritos/', views.get_distritos, name='get_distritos'),
    
    # URL para crear postulación
    path('personas/<int:persona_id>/postulacion/', views.crear_postulacion, name='crear_postulacion'),
    
    # URL para obtener convocatorias
    path('ajax/get-convocatorias/', views.get_convocatorias, name='get_convocatorias'),
    path('ajax/personas-disponibles/', views.buscar_personas_disponibles, name='personas_disponibles'),
    
    # URL para editar postulación
    path('postulaciones/<int:pk>/edit/', views.PostulacionUpdateView.as_view(), name='postulacion_edit'),
    path(
        'postulaciones/<int:pk>/estado/',
        views.actualizar_estado_postulacion_ajax,
        name='postulacion_estado',
    ),
    path(
        'postulaciones/<int:pk>/puntaje/',
        views.actualizar_puntaje_postulacion_ajax,
        name='postulacion_puntaje',
    ),
    
    # URL para registrar colaborador desde postulación
    path('postulaciones/<int:postulacion_id>/registrar-colaborador/', views.registrar_colaborador, name='registrar_colaborador'),
    
    # URL para registro público de postulantes
    path('registro/', views.registro_postulante, name='registro_postulante'),
    path('cv-acceso/<str:token>/', views.cv_acceso_legacy_redirect, name='cv_acceso'),
    path(
        'personas/<int:persona_id>/enlace-cv/',
        views.generar_enlace_cv_postulante,
        name='generar_enlace_cv',
    ),
    
    # URLs para postulante detail y modales
    path('postulante/<int:persona_id>/', views.postulante_detail, name='postulante_detail'),
    path('postulante/<int:persona_id>/agregar-formacion/', views.agregar_formacion, name='agregar_formacion'),
    path('postulante/<int:persona_id>/editar-formacion/<int:formacion_id>/', views.editar_formacion, name='editar_formacion'),
    path('postulante/<int:persona_id>/eliminar-formacion/<int:formacion_id>/', views.eliminar_formacion, name='eliminar_formacion'),
    path('postulante/<int:persona_id>/agregar-curso/', views.agregar_curso, name='agregar_curso'),
    path('postulante/<int:persona_id>/editar-curso/<int:curso_id>/', views.editar_curso, name='editar_curso'),
    path('postulante/<int:persona_id>/eliminar-curso/<int:curso_id>/', views.eliminar_curso, name='eliminar_curso'),
    path('postulante/<int:persona_id>/agregar-experiencia/', views.agregar_experiencia, name='agregar_experiencia'),
    path('postulante/<int:persona_id>/editar-experiencia/<int:experiencia_id>/', views.editar_experiencia, name='editar_experiencia'),
    path('postulante/<int:persona_id>/eliminar-experiencia/<int:experiencia_id>/', views.eliminar_experiencia, name='eliminar_experiencia'),
]
