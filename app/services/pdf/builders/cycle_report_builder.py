from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import tempfile

from app.assets.styles import section_title, sub_title

from app.services.pdf.components.tables import styled_table, styled_table_header, styled_table_multi
from app.services.pdf.components.header import build_header
from app.services.pdf.components.footer import header_footer
from app.services.pdf.utils.formatters import bool_text, clean, format_date, format_list

def build_cycle_report_pdf(data, charts=None):
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(file.name)
    elements = []

    def has_valid_data(table_data, ignore_header=True):
        invalid_values = {
            "no especificado", "no especificada", "no hay notas",
            "nulo", "no realizada", "ninguna", "ninguno", ""
        }
        start_index = 1 if ignore_header else 0

        for row in table_data[start_index:]:
            val = str(row[1] if len(row) > 1 else row[0])
            clean_val = val.strip().lower()
            if clean_val and clean_val not in invalid_values:
                return True
        return False

    user = data["user"]
    history = data["history"]
    mapped = data["mapped_data"]
    cycle = data["cycle"]
    mapped_cycle = data["mapped_cycle"]

    # Encabezado
    title = f"CICLO: {format_date(cycle.start_date)} - {format_date(cycle.end_date)}"
    elements.extend(build_header(title, user, history, sex_biology=mapped["sex_biology"]))

    # Resumen del ciclo
    elements.append(Paragraph("Resumen del periodo", section_title))

    duration = "No especificada"
    end_date = cycle.end_date or datetime.now().date()
    if cycle.start_date:
        duration = f"{(end_date - cycle.start_date).days + 1} días"

    data_table = [
        ["Fecha de inicio", format_date(cycle.start_date)],
        ["Fecha de fin", format_date(end_date)],
        ["Duración", duration]
    ]

    elements.append(styled_table(data_table))
    elements.append(Spacer(1, 20))

    # Registros diarios (detallados)
    logs = mapped_cycle["logs"] if mapped_cycle else []

    if logs:
        elements.append(Paragraph("Registros diarios detallados", section_title))

        for log in logs:
            day_elements = []
            day_elements.append(Paragraph(f"{format_date(log.get('date'))}", sub_title))
            day_elements.append(Spacer(1, 6))

            summary_table = [
                ["Flujo", clean(log.get("menstrual_flow"))],
                ["Cólicos", clean(log.get("cramps"))],
                ["Síntomas", format_list(log.get("symptoms"))]
            ]

            if has_valid_data(summary_table, ignore_header=False):
                day_elements.append(styled_table(summary_table))
                day_elements.append(Spacer(1, 8))

            vital_signs_table = [
                ["Signos vitales", ""],
                ["Presión Arterial", f"{log.get('systolic_bp')}/{log.get('diastolic_bp')}" if log.get("systolic_bp") and log.get("diastolic_bp") else "No especificada"],
                ["Frecuencia Cardíaca", f"{log.get('heart_rate')} bpm" if log.get("heart_rate") else "No especificada"],
                ["Temperatura corporal", f"{log.get('body_temperature')}°C" if log.get("body_temperature") else "No especificada"],
                ["Glucosa", f"{log.get('glycemia')} mg/dL" if log.get("glycemia") else "No especificada"],
            ]

            if has_valid_data(vital_signs_table):
                day_elements.append(styled_table_header(vital_signs_table))
                day_elements.append(Spacer(1, 8))

            habits_table = [
                ["Hábitos y actividades", ""],
                ["Ejercicio", format_list(log.get("exercise"))],
                ["Tiempo de ejercicio", f"{log.get('exercise_time')} minutos" if log.get("exercise_time") else "No especificado"],
                ["Consumo de agua", clean(log.get("water_consumption"))],
                ["Hábitos/Actividades", format_list(log.get("hobbies_activities"))]
            ]

            if has_valid_data(habits_table):
                day_elements.append(styled_table_header(habits_table))
                day_elements.append(Spacer(1, 8))

            reproductive_table = [
                ["Datos reproductivos", ""],
                ["¿Usa anticonceptivos?", bool_text(log.get("anticonceptive_use"))],
                ["Tipo de anticonceptivo", clean(log.get("anticonceptive_type"))],
                ["¿Se encuentra en ventana fértil?", clean(log.get("on_fertile_window"))],
                ["Su fluido vaginal es: ", clean(log.get("vaginal_discharge"))],
            ]

            if has_valid_data(reproductive_table):
                day_elements.append(styled_table_header(reproductive_table))
                day_elements.append(Spacer(1, 8))

            emotional_table = [
                ["Aspectos emocionales", ""],
                ["Nivel de ansiedad", clean(log.get("anxiety"))],
                ["Nivel de estrés", clean(log.get("stress"))],
                ["Estado de ánimo", clean(log.get("mood"))],
                ["Antojo", clean(log.get("cravings"))]
            ]

            if has_valid_data(emotional_table):
                day_elements.append(styled_table_header(emotional_table))
                day_elements.append(Spacer(1, 8))

            test_table = [
                ["Pruebas", ""],
                ["Prueba de embarazo", clean(log.get("pregnancy_test"))],
                ["Prueba de ovulación", clean(log.get("ovulation_test"))]
            ]

            if has_valid_data(test_table):
                day_elements.append(styled_table_header(test_table))
                day_elements.append(Spacer(1, 8))

            notes_val = log.get("notes") if log.get("Notes") else "No hay notas"
            if notes_val and str(notes_val).strip().lower() not in ["no hay notas", "none", "", "string"]:
                day_elements.append(styled_table([["Notas", notes_val]]))
                day_elements.append(Spacer(1, 15))

            # Agregar si hay algo más que el título de la fecha
            if len(day_elements) > 2:
                elements.extend(day_elements)

    # Gráficas
    if charts:
        elements.append(Paragraph("Visualizacón de datos", section_title))
        for name, path in charts.items():
            if path:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(name.capitalize(), sub_title))
                elements.append(Image(path, width=440, height=250))

    # build PDF
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

    return file.name