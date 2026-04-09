from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib import colors

from app.assets.colors import PRIMARY, SECONDARY, LIGHT, DARK
from app.assets.styles import label_style, value_style, sub_title, sub_title_table, sub_title_light

col_widths = [250, 250]

def styled_subtitle(text_content):
    data = [[Paragraph(text_content, sub_title_light)]]
    table = Table(data, colWidths=[500])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(PRIMARY)),
        ('LINEBEFORE', (0, 0), (0, 0), 3, colors.HexColor(PRIMARY)), # Ocultar línea primaria en header
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    return table

# Tabla con encabezado
def styled_table_header(data):
    formatted_data = []

    for i, row in enumerate(data):
        if i == 0:
            formatted_data.append([Paragraph(str(cell), sub_title_table) for cell in row])
        else:
            formatted_data.append([
                Paragraph(str(row[0]), label_style),
                Paragraph(str(row[1]), value_style) if len(row) > 1 else ""
            ])
    table = Table(formatted_data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        # Fondo general y alineación
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(LIGHT)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        # Estilo del Encabezado (Primera fila)
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(LIGHT)),
        ('LINEBEFORE', (0, 0), (0, 0), 3, colors.HexColor(PRIMARY)), # Ocultar línea primaria en header

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),

        # Branding
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor(LIGHT)),
        ('LINEBEFORE', (0, 0), (0, -1), 3, colors.HexColor(PRIMARY)),
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

    table = Table(formatted_data, colWidths=col_widths, repeatRows=0)

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
    formatted_data = []

    for i, row in enumerate(data):
        if i == 0:
            formatted_data.append([Paragraph(str(cell), sub_title) for cell in row])
        else:
            formatted_data.append([
                Paragraph(str(cell), value_style) for cell in row
            ])

    table = Table(formatted_data, repeatRows=0)

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

def charts_table(charts_dict, sub_title_style):
    valid_charts = [(name, path) for name, path in charts_dict.items() if path]
    table_data = []

    # Iterar de 2 en 2 para crear las filas
    for i in range(0, len(valid_charts), 2):
        row = []
        chunk = valid_charts[i:i+2]

        for name, path in chunk:
            # Contenedor de celda: Título + Imagen
            cell = [
                Paragraph(name.capitalize(), sub_title_style),
                Image(path, width=240, height=150)
            ]
            row.append(cell)

        # Relleno si la fila queda incompleta
        if len(row) < 2:
            row.append("")

        table_data.append(row)

    # Definir la tabla con ancho total de 500px (250px por columna)
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    return table