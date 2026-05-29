"""
Permisos de acceso por módulo del menú lateral.
"""
from django.urls import reverse

# Módulos visibles en el menú (clave, etiqueta, url name, icono FontAwesome)
MODULOS_MENU = [
    {'clave': 'inicio', 'label': 'Dashboard', 'url_name': 'master:inicio', 'icon': 'fal fa-home-alt'},
    {'clave': 'convocatorias', 'label': 'Convocatorias', 'url_name': 'master:convocatorias', 'icon': 'fal fa-search'},
    {'clave': 'colaboradores', 'label': 'Empleados', 'url_name': 'master:colaboradores', 'icon': 'fal fa-users'},
    {'clave': 'capacitacion', 'label': 'Aprender', 'url_name': 'master:capacitacion', 'icon': 'fal fa-book-open'},
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
    '/master/ajax/',
    '/master/ajax',
    '/master/registro',
)

PATH_PUBLIC_PREFIXES = (
    '/master/login',
    '/master/registro',
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
    return reverse('master:ajustes')


def get_first_allowed_url(user):
    return get_login_redirect_url(user)


def modulos_labels(modulos_keys):
    labels = {m['clave']: m['label'] for m in MODULOS_MENU}
    labels[MODULO_USUARIOS] = 'Usuarios'
    return [labels.get(k, k) for k in modulos_keys]
