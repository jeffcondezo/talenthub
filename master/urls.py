from django.urls import path
from . import views

app_name = 'master'

urlpatterns = [
    # Página de login
    path('login/', views.CustomLoginView.as_view(), name='login'),
    
    # Página de logout
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Página principal - inducción
    path('induccion/', views.induccion_view, name='induccion'),
    
    # Páginas del sistema
    path('proyecto/', views.proyecto_view, name='proyecto'),
    path('perfiles/', views.perfiles_view, name='perfiles'),
    path('capacitacion/', views.capacitacion_view, name='capacitacion'),
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
    path('personas/<int:id>/delete/', views.PersonaDeleteView.as_view(), name='persona_delete'),
    path('convocatorias/<int:convocatoria_id>/postulantes/', views.PostulantesListView.as_view(), name='postulantes'),
    path('convocatorias/', views.ConvocatoriasListView.as_view(), name='convocatorias'),
    path('convocatorias/create/', views.ConvocatoriaCreateView.as_view(), name='convocatoria_create'),
    path('convocatorias/<int:id>/', views.ConvocatoriaDetailView.as_view(), name='convocatoria_detail'),
    path('convocatorias/<int:id>/edit/', views.ConvocatoriaUpdateView.as_view(), name='convocatoria_edit'),
    path('convocatorias/<int:id>/delete/', views.ConvocatoriaDeleteView.as_view(), name='convocatoria_delete'),
    path('colaboradores/', views.colaboradores_view, name='colaboradores'),
    
    # URLs AJAX para filtrado en cascada de ubicaciones
    path('ajax/get-provincias/', views.get_provincias, name='get_provincias'),
    path('ajax/get-distritos/', views.get_distritos, name='get_distritos'),
    
    # URL para crear postulación
    path('personas/<int:persona_id>/postulacion/', views.crear_postulacion, name='crear_postulacion'),
    
    # URL para obtener convocatorias
    path('ajax/get-convocatorias/', views.get_convocatorias, name='get_convocatorias'),
    
    # URL para editar postulación
    path('postulaciones/<int:pk>/edit/', views.PostulacionUpdateView.as_view(), name='postulacion_edit'),
    
    # URL para registrar colaborador desde postulación
    path('postulaciones/<int:postulacion_id>/registrar-colaborador/', views.registrar_colaborador, name='registrar_colaborador'),
    
    # URL para registro público de postulantes
    path('registro/', views.registro_postulante, name='registro_postulante'),
    
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
