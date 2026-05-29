from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .permissions import (
    PATH_PUBLIC_PREFIXES,
    get_first_allowed_url,
    resolve_modulo_from_path,
    user_has_module,
    user_is_admin,
)


class ModulePermissionMiddleware:
    """
    Exige login en rutas /master/ (salvo públicas) y comprueba permiso por módulo.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if not path.startswith('/master'):
            return self.get_response(request)

        for prefix in PATH_PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return self.get_response(request)

        modulo = resolve_modulo_from_path(path)

        if modulo is None and path.startswith('/master/'):
            if not request.user.is_authenticated:
                return redirect(f'{reverse("master:login")}?next={path}')
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(f'{reverse("master:login")}?next={path}')

        if user_is_admin(request.user):
            return self.get_response(request)

        if modulo == '__unknown__':
            return self.get_response(request)

        if modulo and not user_has_module(request.user, modulo):
            messages.error(
                request,
                'No tiene permiso para acceder a esta sección.',
            )
            return redirect(get_first_allowed_url(request.user))

        return self.get_response(request)
