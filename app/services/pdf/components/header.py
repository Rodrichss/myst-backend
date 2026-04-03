from reportlab.platypus import Paragraph, Spacer, Image, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

from app.services.pdf.utils.formatters import clean, format_full_name

from app.assets.colors import PRIMARY, SECONDARY, LIGHT, DARK
from app.assets.styles import title_style, label_style, value_style, style

def build_header_text(user, history, logo_path=None):
    elements = []

    # Logo opcional
    if logo_path:
        logo = Image(logo_path, width=50, height=50)
        elements.append(logo)

    elements.append(Paragraph("MYST - REPORTE CLÍNICO COMPLETO", title_style))
    elements.append(Spacer(1, 10))

    full_name = format_full_name(user, history)

    elements.append(Paragraph(f"<b>Nombre:</b> {full_name}", value_style))
    elements.append(Paragraph(f"<b>Fecha nacimiento:</b> {history.birthdate}", value_style))
    elements.append(Paragraph(f"<b>Sexo biológico:</b> {history.sex_biology}", value_style))
    elements.append(Paragraph(f"<b>Fecha de reporte:</b> {datetime.now().date()}", value_style))

    elements.append(Spacer(1, 20))

    return elements

def build_header(title, user, history, logo_path=None):
    elements = []

    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 10))

    left = [
        Paragraph(f"<b>Nombre:</b> {format_full_name(user, history)}", style),
        Paragraph(f"<b>Sexo:</b> {clean(history.sex_biology)}", style),
    ]

    right = [
        Paragraph(f"<b>Fecha nacimiento:</b> {clean(history.birthdate)}", style),
        Paragraph(f"<b>Fecha reporte:</b> {datetime.now().date()}", style),
    ]

    logo = Image(logo_path, width=60, height=60) if logo_path else ""

    table = Table(
        [[left, right, logo]],
        colWidths=[200, 200, 80]
    )

    elements.append(table)

    return elements