from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import LETTER
import tempfile

from app.assets.styles import section_title, section_sub_title, sub_title, label_style

from app.services.pdf.components.tables import styled_table, styled_table_multi, charts_table
from app.services.pdf.components.header import build_header
from app.services.pdf.components.footer import header_footer
from app.services.pdf.utils.formatters import bool_text, clean, format_abortions, format_list, format_date, format_stds

# enums
from app.catalogs.scale_enum import ScaleEnum
from app.catalogs.mood_enum import MoodEnum

def build_full_clinical_report_pdf(data, charts):
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    # LETTER es 612pt de ancho. 612 - 500 = 112 / 2 = 56pt de margen cada lado.
    doc = SimpleDocTemplate(
        file.name,
        pagesize=LETTER,
        rightMargin=56,
        leftMargin=56,
        topMargin=50,
        bottomMargin=50
    )
    elements = []

    user = data["user"]
    history = data["history"]
    mapped = data["mapped_data"]
    last_cycle = data["last_cycle"]

    # Encabezado
    elements.extend(build_header("REPORTE CLÍNICO COMPLETO", user, history, sex_biology=mapped["sex_biology"]))

    # Información general
    elements.append(Paragraph("Información general", section_title))

    general_table = [
        ["Sexo legal", clean(mapped["sex_legally"])],
        ["¿Es activ@ sexualmente?", bool_text(history.sexually_active)],
        ["¿Ha tenido abortos?", format_abortions(history.miscarriages_abortions)]
    ]

    elements.append(styled_table(general_table))
    elements.append(Spacer(1, 10))

    # Antecedentes clínicos
    elements.append(Paragraph("Antecedentes clínicos", section_title))

    clinical_table = [
        ["¿Ha sido diagnosticad@ con diabetes?", clean(mapped["diabetes"])],
        ["¿Tiene presión alta (hipertensión)?", bool_text(history.arterial_hypertension)],
        ["¿Ha tenido o tiene algún diagnóstico de depresión?", bool_text(history.depression)],
        ["¿Le han diagnosticado síndrome de ovario poliquístico (PCOS)?", bool_text(history.pcos)],
        ["¿Tiene endometriosis?", bool_text(history.endometriosis)],
        ["¿Ha tenido alguna infección o enfermedad de transmisión sexual (ETS)?", format_stds(mapped["std"])],
    ]

    elements.append(styled_table(clinical_table))
    elements.append(Spacer(1, 10))

    # Sustancias
    elements.append(Paragraph("Habitos y riesgos", section_title))

    substances_table = [
        ["Sustancias que declara consumir:", format_list(mapped['substances'])]
    ]

    elements.append(styled_table(substances_table))
    elements.append(Spacer(1, 10))

    # Ciclo menstrual
    elements.append(Paragraph("Información del ciclo menstrual", section_title))

    cycle_info = [
        ["Promedio ciclo (días)", clean(history.average_menstrual_cycle)],
        ["Regularidad", clean(history.regularity)],
        ["Ciclo actual", format_date(history.last_period_date)]
    ]

    elements.append(styled_table(cycle_info))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph("Usualmente la ovulación ocurre a la mitad del ciclo menstrual", label_style))
    elements.append(Spacer(1, 15))

    # Ultimo ciclo menstrual
    if last_cycle:
        # Logs resumidos (no saturar)
        logs = getattr(last_cycle, "daily_logs", [])

        if logs:
            elements.append(Paragraph("Resumen de registros diarios", section_sub_title))

            log_table = [["Fecha", "Estrés", "Ánimo", "Cólicos"]]

            for log in logs[:10]: # mostrar solo los primeros 10 para no saturar el PDF
                log_table.append([
                    format_date(log.date),
                    clean(ScaleEnum.MAP.get(log.stress)),
                    clean(MoodEnum.MAP.get(log.mood)),
                    clean(ScaleEnum.MAP.get(log.cramps)),
                ])

            elements.append(styled_table_multi(log_table))
    elements.append(Spacer(1, 10))

    # Gráficas
    if charts:
        elements.append(Paragraph("Visualización de datos del último ciclo", section_title))
        elements.append(charts_table(charts, sub_title))

    # build PDF
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

    return file.name