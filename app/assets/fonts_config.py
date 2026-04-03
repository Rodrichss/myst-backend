import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

def register_fonts():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    fonts_path = os.path.abspath(os.path.join(BASE_DIR, "fonts", "Montserrat"))

    pdfmetrics.registerFont(TTFont("Montserrat", os.path.join(fonts_path, "Montserrat-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Montserrat-Bold", os.path.join(fonts_path, "Montserrat-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Montserrat-Italic", os.path.join(fonts_path, "Montserrat-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("Montserrat-BoldItalic", os.path.join(fonts_path, "Montserrat-BoldItalic.ttf")))

    registerFontFamily(
        "Montserrat",
        normal="Montserrat",
        bold="Montserrat-Bold",
        italic="Montserrat-Italic",
        boldItalic="Montserrat-BoldItalic",
    )