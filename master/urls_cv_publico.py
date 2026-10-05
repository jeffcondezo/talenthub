"""URLs públicas del portal CV por token (fuera de /master/, sin login)."""
from django.urls import path

from . import views

app_name = 'cv_publico'

urlpatterns = [
    path('<str:token>/', views.cv_acceso_postulante, name='portal'),
    path(
        '<str:token>/agregar-formacion/',
        views.cv_token_wrap(views.agregar_formacion),
        name='agregar_formacion',
    ),
    path(
        '<str:token>/editar-formacion/<int:formacion_id>/',
        views.cv_token_wrap(views.editar_formacion),
        name='editar_formacion',
    ),
    path(
        '<str:token>/eliminar-formacion/<int:formacion_id>/',
        views.cv_token_wrap(views.eliminar_formacion),
        name='eliminar_formacion',
    ),
    path(
        '<str:token>/agregar-curso/',
        views.cv_token_wrap(views.agregar_curso),
        name='agregar_curso',
    ),
    path(
        '<str:token>/editar-curso/<int:curso_id>/',
        views.cv_token_wrap(views.editar_curso),
        name='editar_curso',
    ),
    path(
        '<str:token>/eliminar-curso/<int:curso_id>/',
        views.cv_token_wrap(views.eliminar_curso),
        name='eliminar_curso',
    ),
    path(
        '<str:token>/agregar-experiencia/',
        views.cv_token_wrap(views.agregar_experiencia),
        name='agregar_experiencia',
    ),
    path(
        '<str:token>/editar-experiencia/<int:experiencia_id>/',
        views.cv_token_wrap(views.editar_experiencia),
        name='editar_experiencia',
    ),
    path(
        '<str:token>/eliminar-experiencia/<int:experiencia_id>/',
        views.cv_token_wrap(views.eliminar_experiencia),
        name='eliminar_experiencia',
    ),
]
