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

