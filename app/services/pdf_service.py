from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

def generate_full_clinical_pdf(data, chart_path=None):

    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(file.name)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    elements.append(Paragraph("Historial Clínico", styles["Title"]))
    elements.append(Spacer(1, 20))

    user = data["user"]
    history = data["history"]
    last_cycle = data["last_cycle"]

    # -------------------------
    # DATOS GENERALES
    # -------------------------
    general_data = [
        ["Campo", "Valor"],
        ["Nombre", user.name],
        ["Apellido", history.last_name],
        ["Fecha nacimiento", str(history.birthdate)],
        ["Sexo biológico", history.sex_biology]
    ]

    table = Table(general_data)
    elements.append(Paragraph("Datos generales", styles["Heading2"]))
    elements.append(table)

    elements.append(Spacer(1, 20))

    # -------------------------
    # ÚLTIMO CICLO
    # -------------------------
    if last_cycle:
        elements.append(Paragraph("Último ciclo menstrual", styles["Heading2"]))

        cycle_data = [
            ["Campo", "Valor"],
            ["Inicio periodo", str(last_cycle.start_date)],
            ["Fin periodo", str(last_cycle.end_date)]
        ]

        elements.append(Table(cycle_data))
        elements.append(Spacer(1, 15))

        # -------------------------
        # DAILY LOGS
        # -------------------------
        logs = last_cycle.daily_logs

        if logs:
            elements.append(Paragraph("Registros diarios del último ciclo", styles["Heading3"]))

            log_table = [["Fecha", "Estrés", "Ansiedad", "Calambres", "Estado de ánimo"]]

            for log in logs:
                log_table.append([
                    str(log.date),
                    str(log.stress),
                    str(log.anxiety),
                    str(log.cramps),
                    log.mood
                ])

            elements.append(Table(log_table))

    elements.append(Spacer(1, 20))

    # -------------------------
    # GRÁFICA
    # -------------------------
    if chart_path:
        elements.append(Paragraph("Gráfica de evolución", styles["Heading2"]))
        elements.append(Image(chart_path, width=400, height=200))

    doc.build(elements)

    return file.name
