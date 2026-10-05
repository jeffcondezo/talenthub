"""
Permisos de acceso por módulo del menú lateral.
"""
import re

from django.urls import reverse

from datetime import date, timedelta

from .models import (
    Persona, FormacionAcademica, CursoEspecializacion, ExperienciaLaboral,
    RegistroActividadSemanal,
)

# Módulos visibles en el menú (clave, etiqueta, url name, icono FontAwesome)
MODULOS_MENU = [
    {'clave': 'inicio', 'label': 'Dashboard', 'url_name': 'master:inicio', 'icon': 'fal fa-home-alt'},
    {'clave': 'convocatorias', 'label': 'Convocatorias', 'url_name': 'master:convocatorias', 'icon': 'fal fa-search'},
    {'clave': 'colaboradores', 'label': 'Empleados', 'url_name': 'master:colaboradores', 'icon': 'fal fa-users'},
    # Oculto de momento: Aprender
    # {'clave': 'capacitacion', 'label': 'Aprender', 'url_name': 'master:capacitacion', 'icon': 'fal fa-book-open'},
    {'clave': 'proyecto', 'label': 'Proyectos', 'url_name': 'master:proyecto', 'icon': 'fal fa-briefcase'},
    {'clave': 'analitica', 'label': 'Analíticas', 'url_name': 'master:analitica', 'icon': 'fal fa-chart-bar'},
]

MODULOS_ASIGNABLES = [m['clave'] for m in MODULOS_MENU]

MODULO_USUARIOS = 'usuarios'

# Prefijos de ruta -> módulo (orden: más específico primero)
PATH_PREFIX_TO_MODULO = [
    ('/master/usuarios/', MODULO_USUARIOS),
    ('/master/usuarios', MODULO_USUARIOS),
    ('/master/convocatorias/', 'convocatorias'),
    ('/master/convocatorias', 'convocatorias'),
    ('/master/postulaciones/', 'convocatorias'),
    ('/master/postulante/', 'convocatorias'),
    ('/master/colaboradores/', 'colaboradores'),
    ('/master/colaboradores', 'colaboradores'),
    ('/master/personas/', 'colaboradores'),
    ('/master/personas', 'colaboradores'),
    ('/master/cv/', 'colaboradores'),
    ('/master/cv', 'colaboradores'),
    ('/master/capacitacion/', 'capacitacion'),
    ('/master/capacitacion', 'capacitacion'),
    ('/master/proyecto/', 'proyecto'),
    ('/master/proyecto', 'proyecto'),
    ('/master/analitica/', 'analitica'),
    ('/master/analitica', 'analitica'),
    ('/master/inicio/', 'inicio'),
    ('/master/inicio', 'inicio'),
    ('/master/induccion/', 'capacitacion'),
    ('/master/induccion', 'capacitacion'),
    ('/master/perfiles/', 'proyecto'),
    ('/master/perfiles', 'proyecto'),
]

# Rutas sin restricción de módulo (None = permitido si autenticado)
PATH_ALWAYS_ALLOWED_PREFIXES = (
    '/master/login',
    '/master/logout',
    '/master/ajustes',
    '/master/mi-perfil',
    '/master/mis-actividades',
    '/master/ajax/',
    '/master/ajax',
    '/master/registro',
)

PATH_PUBLIC_PREFIXES = (
    '/master/login',
    '/master/registro',
    '/master/cv-acceso',
)


def get_perfil_acceso(user):
    if not user or not user.is_authenticated:
        return None
    if getattr(user, 'is_superuser', False):
        return None
    return getattr(user, 'perfil_acceso', None)


def user_is_admin(user):
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_superuser', False):
        return True
    perfil = get_perfil_acceso(user)
    return bool(perfil and perfil.es_administrador)


def get_user_modulos(user):
    """Lista de claves de módulo visibles en menú y permitidos por URL."""
    if not user or not user.is_authenticated:
        return []
    if user_is_admin(user):
        return MODULOS_ASIGNABLES + [MODULO_USUARIOS]
    perfil = get_perfil_acceso(user)
    if perfil is None:
        return []
    return list(perfil.modulos or [])


def user_has_module(user, modulo):
    if modulo is None:
        return True
    if not user or not user.is_authenticated:
        return False
    if user_is_admin(user):
        return True
    if modulo == MODULO_USUARIOS:
        return user_is_admin(user)
    return modulo in get_user_modulos(user)


def resolve_modulo_from_path(path):
    """Resuelve el módulo requerido para una ruta /master/..."""
    if not path.startswith('/master'):
        return None
    for prefix in PATH_ALWAYS_ALLOWED_PREFIXES:
        if path.startswith(prefix):
            return None
    for prefix, modulo in PATH_PREFIX_TO_MODULO:
        if path.startswith(prefix):
            return modulo
    # Rutas /master/ sin match: requerir login pero sin módulo concreto
    if path.startswith('/master/'):
        return '__unknown__'
    return None


def user_has_linked_persona(user):
    """True si la cuenta está vinculada a un registro Persona (empleado)."""
    if not user or not user.is_authenticated:
        return False
    return Persona.objects.filter(user=user).exists()


def get_user_persona(user):
    """Persona vinculada a la cuenta, o None."""
    if not user or not user.is_authenticated:
        return None
    return getattr(user, 'perfil', None)


def user_can_manage_persona_cv(user, persona_id):
    """HR/admin o el propio empleado vinculado."""
    if user_is_admin(user) or user_has_module(user, 'colaboradores'):
        return True
    persona = get_user_persona(user)
    return persona is not None and persona.pk == int(persona_id)


def user_can_access_cv_path(user, path):
    """
    Permite rutas de CV propias sin módulo colaboradores (p. ej. AJAX desde mi-perfil).
    """
    if user_is_admin(user) or user_has_module(user, 'colaboradores'):
        return False
    persona = get_user_persona(user)
    if not persona:
        return False

    m = re.match(r'^/master/cv/(\d+)(?:/|$)', path)
    if m and int(m.group(1)) == persona.pk:
        return True

    m = re.match(r'^/master/personas/(\d+)/cv/', path)
    if m and int(m.group(1)) == persona.pk:
        return True

    delete_checks = [
        (r'^/master/cv/formacion/(\d+)/delete/', FormacionAcademica),
        (r'^/master/cv/curso/(\d+)/delete/', CursoEspecializacion),
        (r'^/master/cv/experiencia/(\d+)/delete/', ExperienciaLaboral),
    ]
    for pattern, model in delete_checks:
        m = re.match(pattern, path)
        if m:
            return model.objects.filter(
                pk=int(m.group(1)),
                cv__persona_id=persona.pk,
            ).exists()

    return False


def user_can_manage_own_actividades(user, persona_id=None):
    """Admin o el empleado vinculado a su propio registro de actividades."""
    if user_is_admin(user):
        return True
    persona = get_user_persona(user)
    if not persona:
        return False
    if persona_id is None:
        return True
    return persona.pk == int(persona_id)


def calcular_limites_semana_iso(anio, semana):
    """Devuelve (fecha_inicio, fecha_fin) para una semana ISO."""
    fecha_inicio = date.fromisocalendar(anio, semana, 1)
    fecha_fin = date.fromisocalendar(anio, semana, 7)
    return fecha_inicio, fecha_fin


def semana_iso_desplazada(anio, semana, delta_semanas):
    """Desplaza una semana ISO por delta_semanas (negativo = anterior)."""
    base = date.fromisocalendar(anio, semana, 1) + timedelta(weeks=delta_semanas)
    iso = base.isocalendar()
    return iso[0], iso[1]


def get_or_create_registro_semana(persona, anio, semana):
    """Obtiene o crea el registro semanal de actividades de una persona."""
    fecha_inicio, fecha_fin = calcular_limites_semana_iso(anio, semana)
    registro, _ = RegistroActividadSemanal.objects.get_or_create(
        persona=persona,
        anio=anio,
        semana=semana,
        defaults={
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        },
    )
    return registro


def get_login_redirect_url(user):
    modulos = get_user_modulos(user)
    orden = MODULOS_ASIGNABLES + ([MODULO_USUARIOS] if user_is_admin(user) else [])
    for clave in orden:
        if clave in modulos:
            for item in MODULOS_MENU:
                if item['clave'] == clave:
                    return reverse(item['url_name'])
            if clave == MODULO_USUARIOS:
                return reverse('master:usuarios_list')
    if user_has_linked_persona(user):
        return reverse('master:mi_perfil')
    return reverse('master:ajustes')


def get_first_allowed_url(user):
    return get_login_redirect_url(user)


def modulos_labels(modulos_keys):
    labels = {m['clave']: m['label'] for m in MODULOS_MENU}
    labels[MODULO_USUARIOS] = 'Usuarios'
    return [labels.get(k, k) for k in modulos_keys]
