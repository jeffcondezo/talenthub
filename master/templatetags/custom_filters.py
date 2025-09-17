from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Filtro personalizado para agregar clases CSS a campos de formulario
    """
    return field.as_widget(attrs={'class': css_class})

