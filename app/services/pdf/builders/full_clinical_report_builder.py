from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import tempfile, os
from datetime import datetime

from app.assets.colors import PRIMARY, SECONDARY, LIGHT, DARK
from app.assets.styles import section_title, sub_title, text

from app.services.pdf.components.tables import styled_table, styled_table_multi
from app.services.pdf.components.header import build_header
from app.services.pdf.components.footer import header_footer
from app.services.pdf.utils.formatters import bool_text, clean, format_abortions, format_list

# enums
from app.catalogs.scale_enum import ScaleEnum
from app.catalogs.mood_enum import MoodEnum

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "myst_logo.png")

def build_full_clinical_report_pdf(data, charts):
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(file.name)
    elements = []

    user = data["user"]
    history = data["history"]
    mapped = data["mapped_data"]
    last_cycle = data["last_cycle"]

    # Encabezado
    elements.extend(build_header("REPORTE CLÍNICO COMPLETO", user, history, logo_path=LOGO_PATH))

    # Información general
    elements.append(Paragraph("Información general", section_title))

    general_table = [
        ["Sexo legal", clean(history.sex_legally)],
        ["¿Es activ@ sexualmente?", bool_text(history.sexually_active)],
        ["¿Ha tenido abortos?", format_abortions(history.miscarriages_abortions)]
    ]

    elements.append(styled_table(general_table))
    elements.append(Spacer(1, 20))

    # Antecedentes clínicos
    elements.append(Paragraph("Antecedentes clínicos", section_title))

    clinical_table = [
        ["¿Ha sido diagnosticada con diabetes?", clean(mapped["diabetes"])],
        ["¿Tiene presión alta (hipertensión)?", bool_text(history.arterial_hypertension)],
        ["¿Ha tenido o tiene algún diagnóstico de depresión?", bool_text(history.depression)],
        ["¿Le han diagnosticado síndrome de ovario poliquístico (PCOS)?", bool_text(history.pcos)],
        ["¿Tiene endometriosis?", bool_text(history.endometriosis)],
        ["¿Ha tenido alguna infección o enfermedad de transmisión sexual (ETS)?", clean(mapped["std"])],
    ]

    elements.append(styled_table(clinical_table))
    elements.append(Spacer(1, 20))

    # Sustancias
    elements.append(Paragraph("Habitos y riesgos", section_title))

    substances_table = [
        ["Sustancias que declara consumir:", format_list(mapped['substances'])]
    ]

    elements.append(styled_table(substances_table))
    elements.append(Spacer(1, 20))

    # Ciclo menstrual
    elements.append(Paragraph("Información del ciclo menstrual", section_title))

    cycle_info = [
        ["Promedio ciclo (días)", clean(history.average_menstrual_cycle)],
        ["Ovulación estimada", clean(history.average_ovulation)]
    ]

    elements.append(styled_table(cycle_info))
    elements.append(Spacer(1, 20))

    # Ultimo ciclo menstrual
    if last_cycle:
        elements.append(Paragraph("Último ciclo menstrual", section_title))

        cycle_table = [
            ["Fecha de inicio", str(last_cycle.start_date)],
            ["Fecha de fin", str(last_cycle.end_date)]
        ]

        elements.append(styled_table(cycle_table))
        elements.append(Spacer(1, 15))

        # Logs resumidos (no saturar)
        logs = getattr(last_cycle, "daily_logs", [])

        if logs:
            elements.append(Paragraph("Resumen de registros diarios", sub_title))

            log_table = [["Fecha", "Estrés", "Ánimo", "Cólicos"]]

            for log in logs[:10]: # mostrar solo los primeros 10 para no saturar el PDF
                log_table.append([
                    clean(log.date),
                    clean(ScaleEnum.MAP.get(log.stress)),
                    clean(MoodEnum.MAP.get(log.mood)),
                    clean(ScaleEnum.MAP.get(log.cramps)),
                ])

            elements.append(styled_table_multi(log_table))
    elements.append(Spacer(1, 20))

    # GRÁFICAS
    if charts:
        elements.append(Paragraph("Gráficas del ciclo", section_title))

        for name, path in charts.items():
            if path:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(name.capitalize(), sub_title))
                elements.append(Image(path, width=440, height=250))

    # build PDF
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

    return file.name