"""Generación de PDF para el registro semanal de actividades."""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _p(text, style):
    """Escapa texto para Paragraph de ReportLab."""
    if text is None:
        return Paragraph('—', style)
    safe = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return Paragraph(safe, style)


def generar_actividades_semanales_pdf(persona, registro, actividades):
    """Devuelve bytes del PDF del registro semanal."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f'Actividades semana {registro.semana}/{registro.anio}',
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleTalent',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#0f766e'),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'SubtitleTalent',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=4,
    )
    cell_style = ParagraphStyle(
        'CellTalent',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
    )
    header_cell_style = ParagraphStyle(
        'HeaderCellTalent',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.white,
    )

    story = [
        Paragraph('TalentHub — Registro semanal de actividades', title_style),
        Paragraph(
            f'<b>{persona.nombre_completo}</b> · Semana {registro.semana} / {registro.anio} · '
            f'{registro.fecha_inicio.strftime("%d/%m/%Y")} — {registro.fecha_fin.strftime("%d/%m/%Y")}',
            subtitle_style,
        ),
        Spacer(1, 0.4 * cm),
    ]

    if actividades:
        header = [
            _p('Fecha', header_cell_style),
            _p('Grupo', header_cell_style),
            _p('Tipo de actividad', header_cell_style),
            _p('Cliente / Proyecto', header_cell_style),
            _p('Descripción', header_cell_style),
        ]
        rows = [header]
        for actividad in actividades:
            rows.append([
                _p(actividad.fecha.strftime('%d/%m/%Y'), cell_style),
                _p(actividad.get_grupo_display_label(), cell_style),
                _p(actividad.get_tipo_display_label(), cell_style),
                _p(actividad.cliente_proyecto or '—', cell_style),
                _p(actividad.descripcion or '—', cell_style),
            ])

        col_widths = [2.2 * cm, 3.2 * cm, 5.5 * cm, 4.5 * cm, 11 * cm]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(
            f'Total: {len(actividades)} actividad{"es" if len(actividades) != 1 else ""}.',
            subtitle_style,
        ))
    else:
        story.append(Paragraph(
            'No hay actividades registradas para esta semana.',
            ParagraphStyle(
                'EmptyTalent',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#64748b'),
                spaceBefore=20,
                spaceAfter=20,
            ),
        ))

    doc.build(story)
    return buffer.getvalue()
