from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors

from app.assets.colors import PRIMARY, SECONDARY, LIGHT, DARK
from app.assets.styles import label_style, value_style

# Tabla con encabezado
def styled_table_header(data):
    table = Table(data, colWidths=[220,230])
    style = TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(SECONDARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(LIGHT)),

        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(LIGHT)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(DARK)),

        # Alignment and fonts
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ('FONTNAME', (0, 0), (-1, 0), 'Montserrat-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Montserrat'),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),

        # Grid
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor(LIGHT)),
        ('GRID', (0, 1), (-1, -1), 0.3, colors.HexColor(LIGHT)),
    ])
    table.setStyle(style)
    return table

# Tabla predeterminada
def styled_table(data):
    formatted_data = []

    for label, value in data:
        formatted_data.append([
            Paragraph(str(label), label_style),
            Paragraph(str(value), value_style)
        ])

    table = Table(formatted_data, colWidths=[260,180])

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(LIGHT)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),

        # Branding
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor(LIGHT)),
        ('LINEBEFORE', (0, 0), (0, -1), 3, colors.HexColor(PRIMARY)),
    ])
    table.setStyle(style)
    return table

def styled_table_multi(data):
    formatted = []

    for row in data:
        formatted.append([
            Paragraph(str(cell), value_style) for cell in row
        ])

    table = Table(formatted)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(SECONDARY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(DARK)),

        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor(SECONDARY)),

        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    return table