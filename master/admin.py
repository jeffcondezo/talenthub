from django.contrib import admin

from .models import (
    RegistroActividadSemanal, ActividadSemanal, AccesoCVPostulante,
    Skill, PersonaSkill, Proyecto, ProyectoSkill, AsignacionProyecto,
)


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


@admin.register(AccesoCVPostulante)
class AccesoCVPostulanteAdmin(admin.ModelAdmin):
    list_display = ('persona', 'activo', 'fecha_expiracion', 'ultimo_acceso', 'convocatoria')
    list_filter = ('activo',)
    search_fields = ('persona__nombres', 'persona__apellido_paterno', 'token')
    readonly_fields = ('token', 'fecha_creacion', 'ultimo_acceso')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre',)


@admin.register(PersonaSkill)
class PersonaSkillAdmin(admin.ModelAdmin):
    list_display = ('persona', 'skill', 'nivel', 'registrado_por', 'fecha_actualizacion')
    list_filter = ('nivel', 'skill')
    search_fields = (
        'persona__nombres',
        'persona__apellido_paterno',
        'skill__nombre',
    )


class ProyectoSkillInline(admin.TabularInline):
    model = ProyectoSkill
    extra = 1


class AsignacionProyectoInline(admin.TabularInline):
    model = AsignacionProyecto
    extra = 0
    raw_id_fields = ('colaborador',)


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'cliente', 'estado', 'fecha_inicio', 'fecha_actualizacion')
    list_filter = ('estado',)
    search_fields = ('codigo', 'nombre', 'cliente')
    inlines = [ProyectoSkillInline, AsignacionProyectoInline]


@admin.register(AsignacionProyecto)
class AsignacionProyectoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'colaborador', 'horas_semanales', 'rol', 'activo')
    list_filter = ('activo', 'proyecto')
    search_fields = (
        'proyecto__nombre',
        'colaborador__persona__nombres',
        'colaborador__persona__apellido_paterno',
    )
