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
        ["Apellido", user.last_name],
        ["Fecha nacimiento", str(user.birth_date)],
        ["Sexo biológico", history.biological_sex]
    ]

    table = Table(general_data)
    elements.append(Paragraph("Datos generales", styles["Heading2"]))
    elements.append(table)

    elements.append(Spacer(1, 20))

    # -------------------------
    # ÚLTIMO CICLO
    # -------------------------
    if last_cycle:
        cycle_data = [
            ["Campo", "Valor"],
            ["Estrés", last_cycle.stress],
            ["Ansiedad", last_cycle.anxiety],
            ["Calambres", last_cycle.cramps],
            ["Inicio periodo", str(last_cycle.period_start_date)],
            ["Fin periodo", str(last_cycle.period_end_date)]
        ]

        elements.append(Paragraph("Último ciclo menstrual", styles["Heading2"]))
        elements.append(Table(cycle_data))

    elements.append(Spacer(1, 20))

    # -------------------------
    # GRÁFICA
    # -------------------------
    if chart_path:
        elements.append(Paragraph("Gráfica de evolución", styles["Heading2"]))
        elements.append(Image(chart_path, width=400, height=200))

    doc.build(elements)

    return file.name