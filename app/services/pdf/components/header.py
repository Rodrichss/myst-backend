from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle
from datetime import datetime

from app.services.pdf.utils.formatters import clean, format_full_name
from app.assets.styles import title_style, style

def build_header(title, user, history, logo_path=None):
    elements = []

    col_widths = [170, 170, 100]

    left_info = [
        Paragraph(f"<b>Nombre:</b> {format_full_name(user, history)}", style),
        Paragraph(f"<b>Sexo:</b> {clean(history.sex_biology)}", style),
    ]

    right_info = [
        Paragraph(f"<b>Fecha nacimiento:</b> {clean(history.birthdate)}", style),
        Paragraph(f"<b>Fecha reporte:</b> {datetime.now().date()}", style),
    ]

    logo = Image(logo_path, width=80, height=80) if logo_path else ""

    # Estructura de la tabla:
    # Fila 0: [Título (que se extenderá), vacío, Logo (que ocupa 2 filas)]
    # Fila 1: [Datos Izquierda, Datos Derecha, (espacio del logo)]
    data = [
        [Paragraph(title, title_style), "", logo],
        [left_info, right_info, ""]
    ]

    table = Table(
        data,
        colWidths=col_widths
    )

    table.setStyle(TableStyle([
        # Combinamos el título (Fila 0, Col 0 a Col 1)
        ('SPAN', (0, 0), (1, 0)),

        # Combinamos el logo verticalmente (Fila 0 a 1, Col 2)
        ('SPAN', (2, 0), (2, 1)),

        # Alineaciones
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (2, 1), 'RIGHT'), # Logo a la derecha

        # Opcional: Debugging (descomenta la siguiente línea para ver los bordes)
        # ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))

    return elements