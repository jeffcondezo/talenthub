from django.contrib import admin
from .models import Area, Especialidad, Proyecto


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'fecha_creacion')
    search_fields = ('nombre',)


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'slug', 'estado', 'fecha_creacion')
    list_filter = ('area', 'estado')
    search_fields = ('nombre', 'descripcion')
    autocomplete_fields = ('area',)
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion',)


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad', 'estado', 'fecha_inicio', 'fecha_fin', 'fecha_creacion')
    list_filter = ('estado', 'especialidad', 'especialidad__area')
    search_fields = ('nombre', 'descripcion')
    autocomplete_fields = ('especialidad',)
    filter_horizontal = ('colaboradores',)
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion',)
