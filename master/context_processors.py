from .permissions import MODULOS_MENU, get_user_modulos, user_is_admin


def permisos_menu(request):
    user = request.user
    if user.is_authenticated:
        return {
            'user_es_admin': user_is_admin(user),
            'user_modulos': get_user_modulos(user),
            'modulos_menu': MODULOS_MENU,
        }
    return {
        'user_es_admin': False,
        'user_modulos': [],
        'modulos_menu': MODULOS_MENU,
    }
