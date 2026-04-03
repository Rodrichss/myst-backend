def header_footer(canvas, doc):
    canvas.saveState()

    canvas.setFont('Montserrat', 8)
    canvas.drawString(
        40, 30,
        "Este reporte es generado por Myst. No sustituye diagnóstico médico profesional."
    )

    canvas.drawString(
        40, 20,
        "La responsabilidad del uso de esta información recae en la usuaria."
    )
    canvas.restoreState()