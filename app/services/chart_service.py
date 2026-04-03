import matplotlib.pyplot as plt
import tempfile

def generate_cycle_charts(last_cycle):
    charts = {}

    if not last_cycle or not last_cycle.daily_logs:
        return charts

    logs = sorted(last_cycle.daily_logs, key=lambda x: x.date)

    def build_chart(values, title, ylabel):
        dates = [log.date for log in logs if getattr(log, values) is not None]
        data_values = [getattr(log, values) for log in logs if getattr(log, values) is not None]

        if not dates or not data_values:
            return None

        plt.figure()
        plt.plot(dates, data_values)
        plt.title(title)
        plt.xlabel("Fecha")
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.tight_layout()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(tmp.name)
        plt.close()

        return tmp.name

    charts["stress"] = build_chart("stress", "Estrés diario", "Nivel")
    charts["anxiety"] = build_chart("anxiety", "Ansiedad diaria", "Nivel")
    charts["cramps"] = build_chart("cramps", "Calambres diarios", "Intensidad")
    charts["mood"] = build_chart("mood", "Estado de ánimo", "Escala")
    charts["temperature"] = build_chart("body_temperature", "Temperatura corporal", "°C")

    return charts