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
    path('cv/<str:tipo>/<int:id>/', views.CVDetailView.as_view(), name='cv_detail'),
    
    # URLs para gestión de CV
    path('cv/<str:tipo>/<int:persona_id>/formacion/', views.FormacionAcademicaCreateView.as_view(), name='cv_formacion_create'),
    path('cv/<str:tipo>/<int:persona_id>/formacion/<int:formacion_id>/', views.FormacionAcademicaUpdateView.as_view(), name='cv_formacion_edit'),
    path('cv/formacion/<int:formacion_id>/delete/', views.FormacionAcademicaDeleteView.as_view(), name='cv_formacion_delete'),
    
    path('cv/<str:tipo>/<int:persona_id>/curso/', views.CursoEspecializacionCreateView.as_view(), name='cv_curso_create'),
    path('cv/<str:tipo>/<int:persona_id>/curso/<int:curso_id>/', views.CursoEspecializacionUpdateView.as_view(), name='cv_curso_edit'),
    path('cv/curso/<int:curso_id>/delete/', views.CursoEspecializacionDeleteView.as_view(), name='cv_curso_delete'),
    
    path('cv/<str:tipo>/<int:persona_id>/experiencia/', views.ExperienciaLaboralCreateView.as_view(), name='cv_experiencia_create'),
    path('cv/<str:tipo>/<int:persona_id>/experiencia/<int:experiencia_id>/', views.ExperienciaLaboralUpdateView.as_view(), name='cv_experiencia_edit'),
    path('cv/experiencia/<int:experiencia_id>/delete/', views.ExperienciaLaboralDeleteView.as_view(), name='cv_experiencia_delete'),
    path('aspirantes/', views.AspirantesListView.as_view(), name='aspirantes'),
    path('aspirantes/create/', views.AspiranteCreateView.as_view(), name='aspirante_create'),
    path('aspirantes/<int:id>/', views.AspiranteDetailView.as_view(), name='aspirante_detail'),
    path('aspirantes/<int:id>/edit/', views.AspiranteUpdateView.as_view(), name='aspirante_edit'),
    path('aspirantes/<int:id>/delete/', views.AspiranteDeleteView.as_view(), name='aspirante_delete'),
    path('convocatorias/', views.ConvocatoriasListView.as_view(), name='convocatorias'),
    path('convocatorias/<int:id>/', views.ConvocatoriaDetailView.as_view(), name='convocatoria_detail'),
    path('convocatorias/<int:id>/edit/', views.ConvocatoriaUpdateView.as_view(), name='convocatoria_edit'),
    path('convocatorias/<int:id>/delete/', views.ConvocatoriaDeleteView.as_view(), name='convocatoria_delete'),
    path('colaboradores/', views.colaboradores_view, name='colaboradores'),
]
