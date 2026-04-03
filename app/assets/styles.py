from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

from app.assets.colors import PRIMARY, SECONDARY, LIGHT, DARK

# Estilos
style = ParagraphStyle(
        name="Header",
        fontName="Montserrat",
        fontSize=10,
        textColor=colors.HexColor(DARK),
        leading=14
    )

title_style = ParagraphStyle(
    name="Title",
    fontName="Montserrat-Bold",
    fontSize=18,
    textColor=colors.HexColor(PRIMARY),
    leading=14
)

label_style = ParagraphStyle(
    name="Label",
    fontName="Montserrat-Bold",
    fontSize=10,
    textColor=colors.HexColor(DARK),
    leading=12,
    wordWrap='CJK'
)

value_style = ParagraphStyle(
    name="Value",
    fontName="Montserrat",
    fontSize=10,
    textColor=colors.HexColor(DARK),
    leading=12,
    wordWrap='CJK'
)

section_title = ParagraphStyle(
    name="SectionTitle",
    fontName="Montserrat-Bold",
    fontSize=14,
    textColor=colors.HexColor(PRIMARY),
    spaceAfter=10,
    spaceBefore=10
)

sub_title = ParagraphStyle(
    name="SubTitle",
    fontName="Montserrat-Bold",
    fontSize=11,
    textColor=colors.HexColor(DARK),
    spaceAfter=6
)

text = ParagraphStyle(
    name="Text",
    fontName="Montserrat",
    fontSize=11,
    textColor=colors.HexColor(DARK),
    spaceAfter=3
)
