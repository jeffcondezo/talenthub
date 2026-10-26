"""
Catálogo de grupos y tipos de actividad semanal.
"""

GRUPO_CONSULTORIA = 'CONSULTORIA'
GRUPO_COMERCIAL = 'COMERCIAL'
GRUPO_CONSULTORIA_BI = 'CONSULTORIA_BI'

GRUPO_CHOICES = [
    (GRUPO_CONSULTORIA, 'Consultoría técnica'),
    (GRUPO_COMERCIAL, 'Comercial y gestión de proyecto'),
    (GRUPO_CONSULTORIA_BI, 'Consultoría en BI'),
]

TIPOS_POR_GRUPO = {
    GRUPO_CONSULTORIA: [
        ('REUNION_RELEVAMIENTO', 'Reunión de relevamiento'),
        ('REUNION_INTERNA', 'Reunión interna'),
        ('REUNION_REVISION_PROPUESTA', 'Reunión interna de revisión de propuesta'),
        ('ELABORACION_PRESENTACION_PROPUESTA', 'Elaboración de presentación para propuesta'),
        ('CAPACITACION_CONSULTORIA', 'Capacitación de consultoría'),
        ('DESARROLLO_PROPUESTA_TECNICA', 'Desarrollo de propuesta técnica'),
        ('PROGRAMACION_PROYECTO', 'Actividades de programación para un proyecto'),
        ('PROGRAMACION_MESA_AYUDA', 'Actividades de programación para una solicitud por mesa de ayuda'),
        ('DOCUMENTACION_PROYECTO', 'Elaboración de documentación de proyecto'),
        ('CAPACITACION_CLIENTES', 'Capacitación a los clientes'),
    ],
    GRUPO_CONSULTORIA_BI: [
        # Catálogo desde libro1.xlsx (únicos, sin repetidos)
        ('BI_REV_REQ_FUNCIONALES', 'Revisión con usuarios requerimientos funcionales'),
        ('BI_CREACION_MODELO_CONCEPTUAL', 'Creación modelo conceptual'),
        ('BI_ELABORAR_REF', 'Elaborar Reporte Especificaciones Funcionales (REF)'),
        ('BI_REVISAR_REF', 'Revisar Reporte Especificaciones Funcionales'),
        ('BI_AJUSTES_DOCUMENTOS', 'Realizar Ajustes a Documentos'),
        ('BI_MAPEAR_FUENTES_DATOS', 'Mapear las Fuentes de Datos'),
        ('BI_DISENO_FISICO_MODELO_DATOS', 'Realizar Diseño Físico del Modelo de Datos'),
        ('BI_REVISAR_MODELO_FISICO', 'Revisar Modelo Físico'),
        ('BI_AJUSTES_MODELO_FISICO', 'Realizar Ajustes al Modelo Físico'),
        ('BI_FASE_DEF_MODELO_SOLUCION', 'Fase de Definición del Modelo de la Solución Terminado'),
        ('BI_ELABORAR_RET', 'Elaborar Documento Especificaciones Técnicas (RET)'),
        ('BI_REVISAR_RET', 'Revisar Documento de Especificaciones Técnicas'),
        ('BI_ELABORAR_DISENO_TABLEROS', 'Elaborar Documento de Diseño de Tableros'),
        ('BI_REVISAR_DISENO_TABLEROS', 'Revisar Documento de Diseño de Tableros'),
        ('BI_AJUSTES_DISENO_TABLEROS', 'Ajustes Documento de Diseño de Tableros'),
        ('BI_DESARROLLO_TABLERO_POWER_BI', 'Desarrollo Tablero en Power BI'),
        ('BI_REUNIONES_RELEVAMIENTO_FUNC', 'Reuniones de Relevamiento Funcional'),
        ('BI_ELABORAR_REF_SIN_SIGLA', 'Elaborar Reporte Especificaciones Funcionales'),
        ('BI_DOCUMENTOS_APROBADOS', 'Documentos Aprobados'),
        ('BI_FASE_PLANIFICACION_TERMINADA', 'Fase de Planificación Terminada'),
        ('BI_ANALISIS_FUENTES_DATOS', 'Análisis fuentes de datos'),
        ('BI_DISENO_FISICO_MODELO_DWH', 'Realizar Diseño Físico del Modelo de Datos DWH'),
        ('BI_ELABORAR_RET_SIN_SIGLA', 'Elaborar Documento Especificaciones Técnicas'),
        ('BI_FASE_DESARROLLO_CARGA', 'Fase de Desarrollo de Procesos de Carga Terminado'),
        ('BI_DESARROLLO_TABLERO_STRATEGY', 'Desarrollo Tablero en Strategy'),
    ],
    GRUPO_COMERCIAL: [
        ('PROSPECCION_CLIENTES', 'Prospección de nuevos clientes'),
        ('INVESTIGACION_CUENTA', 'Investigación de cuenta objetivo'),
        ('PREPARACION_REUNION_COMERCIAL', 'Preparación de reunión comercial'),
        ('REUNION_PRESENTACION_INSTITUCIONAL', 'Reunión de presentación institucional'),
        ('DIAGNOSTICO_INICIAL', 'Diagnóstico inicial de necesidad'),
        ('LEVANTAMIENTO_PROCESOS', 'Levantamiento de procesos actuales'),
        ('IDENTIFICACION_PAIN_POINTS', 'Identificación de pain points'),
        ('MAPEO_STAKEHOLDERS', 'Mapeo de stakeholders'),
        ('ALCANCE_PRELIMINAR', 'Definición de alcance preliminar'),
        ('MATRIZ_REQUERIMIENTOS', 'Matriz de requerimientos'),
        ('VIABILIDAD_TECNICA', 'Análisis de viabilidad técnica'),
        ('ESTIMACION_ESFUERZO', 'Estimación de esfuerzo'),
        ('IDENTIFICACION_RIESGOS', 'Identificación de riesgos'),
        ('PROPUESTA_ECONOMICA', 'Elaboración de propuesta económica'),
        ('REVISION_PRICING', 'Revisión de pricing y rentabilidad'),
        ('SEGUIMIENTO_PROPUESTA', 'Seguimiento de propuesta enviada'),
        ('NEGOCIACION_COMERCIAL', 'Negociación comercial'),
        ('COORDINACION_CONTRATO', 'Coordinación de contrato / SOW / NDA'),
        ('COORDINACION_ORDEN_COMPRA', 'Coordinación de orden de compra o aprobación formal'),
        ('KICKOFF_INTERNO', 'Kickoff interno'),
        ('KICKOFF_CLIENTE', 'Kickoff con cliente'),
        ('CRONOGRAMA_PROYECTO', 'Elaboración de cronograma de proyecto'),
        ('SEGUIMIENTO_SEMANAL_PROYECTO', 'Seguimiento semanal del proyecto'),
        ('GESTION_PENDIENTES_CLIENTE', 'Gestión de pendientes del cliente'),
        ('CONTROL_CAMBIOS_ALCANCE', 'Control de cambios de alcance'),
        ('REVISION_ENTREGABLES_INTERNOS', 'Revisión de entregables internos'),
        ('APROBACION_ENTREGABLES', 'Gestión de aprobación de entregables'),
        ('CONTROL_HITOS_FACTURACION', 'Control de hitos de facturación'),
        ('SEGUIMIENTO_CUENTAS_COBRAR', 'Seguimiento de cuentas por cobrar'),
        ('CIERRE_PROYECTO', 'Reunión de cierre de proyecto'),
        ('PERIODO_GARANTIA', 'Activación de periodo de garantía'),
        ('CONTINUIDAD_SERVICIO', 'Reunión de continuidad de servicio'),
        ('UPSELLING_CROSS_SELLING', 'Identificación de upselling y cross-selling'),
    ],
}

ALL_TIPO_CHOICES = []
for _grupo, tipos in TIPOS_POR_GRUPO.items():
    ALL_TIPO_CHOICES.extend(tipos)


def tipos_validos_para_grupo(grupo):
    """Devuelve lista de claves de tipo válidas para un grupo."""
    return [clave for clave, _ in TIPOS_POR_GRUPO.get(grupo, [])]


def get_tipo_label(grupo, tipo):
    """Etiqueta legible de un tipo dentro de un grupo."""
    for clave, label in TIPOS_POR_GRUPO.get(grupo, []):
        if clave == tipo:
            return label
    return tipo


def get_grupo_label(grupo):
    """Etiqueta legible de un grupo."""
    for clave, label in GRUPO_CHOICES:
        if clave == grupo:
            return label
    return grupo


def tipo_pertenece_a_grupo(grupo, tipo):
    """Verifica si un tipo pertenece al grupo indicado."""
    return tipo in tipos_validos_para_grupo(grupo)
