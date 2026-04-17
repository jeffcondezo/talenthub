from django import template
import os

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Filtro personalizado para agregar clases CSS a campos de formulario
    """
    return field.as_widget(attrs={'class': css_class})

@register.filter
def basename(value):
    """
    Filtro para obtener solo el nombre del archivo de una ruta
    """
    if value:
        return os.path.basename(str(value))
    return ''


@register.filter
def iniciales(value):
    """
    Obtiene las iniciales del nombre completo (ej: "Ana Salinas" -> "AS").
    Toma la primera letra del primer nombre y la primera del último apellido.
    """
    if not value:
        return ''
    name = str(value).strip()
    if not name:
        return ''
    words = name.split()
    if len(words) >= 2:
        return (words[0][0] + words[-1][0]).upper()
    return (name[:2] if len(name) >= 2 else name[0]).upper()

