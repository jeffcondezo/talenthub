from django.contrib import admin

from .models import RegistroActividadSemanal, ActividadSemanal


class ActividadSemanalInline(admin.TabularInline):
    model = ActividadSemanal
    extra = 0
    fields = ('fecha', 'grupo', 'tipo', 'cliente_proyecto', 'descripcion')


@admin.register(RegistroActividadSemanal)
class RegistroActividadSemanalAdmin(admin.ModelAdmin):
    list_display = ('persona', 'anio', 'semana', 'fecha_inicio', 'fecha_fin', 'fecha_actualizacion')
    list_filter = ('anio', 'semana')
    search_fields = (
        'persona__nombres',
        'persona__apellido_paterno',
        'persona__numero_documento',
    )
    inlines = [ActividadSemanalInline]


@admin.register(ActividadSemanal)
class ActividadSemanalAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'get_grupo_display_label', 'get_tipo_display_label', 'cliente_proyecto', 'registro')
    list_filter = ('grupo', 'fecha')
    search_fields = ('cliente_proyecto', 'descripcion', 'registro__persona__nombres')
