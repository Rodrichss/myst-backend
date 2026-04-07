import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tempfile
import textwrap

from app.assets.colors import PRIMARY, SECONDARY, LIGHT, DARK

from app.catalogs.mood_enum import MoodEnum
from app.catalogs.scale_enum import ScaleEnum

def generate_cycle_charts(last_cycle):
    charts = {}
    logs = getattr(last_cycle, "daily_logs", []) if last_cycle else []

    if not logs:
        return charts

    logs = sorted(logs, key=lambda x: x.date)

    # mapping campo → enum
    ENUM_FIELDS = {
        "mood": MoodEnum,
        "stress": ScaleEnum,
        "anxiety": ScaleEnum,
        "cramps": ScaleEnum,
    }

    def apply_enum_labels(field):
        enum = ENUM_FIELDS.get(field)

        if not enum:
            return

        keys = list(enum.MAP.keys())
        labels = [textwrap.fill(label, width=12) for label in enum.MAP.values()]

        plt.yticks(keys, labels)

    def build_chart(field, title, ylabel, color=PRIMARY):
        dates = []
        values = []

        for log in logs:
            value = getattr(log, field, None)
            if value is not None:
                dates.append(log.date)
                values.append(value)

        if not dates or not values:
            return None

        plt.figure()
        plt.plot(dates, values, marker="o", color=color, linestyle='-', linewidth=2)

        # Formatear para que solo muestre día/mes
        ax = plt.gca() # Obtener los ejes actuales
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

        plt.title(title)
        plt.xlabel("Fecha")
        plt.ylabel(textwrap.fill(ylabel, width=15))

        # aplicar labels si es enum
        apply_enum_labels(field)

        plt.xticks(rotation=45)
        plt.tight_layout()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(tmp.name)
        plt.close()

        return tmp.name

    charts["Estrés"] = build_chart("stress", "Estrés diario", "Nivel", color=PRIMARY)
    charts["Ansiedad"] = build_chart("anxiety", "Ansiedad diaria", "Nivel", color=SECONDARY)
    charts["Cólicos"] = build_chart("cramps", "Cólicos diarios", "Intensidad", color=PRIMARY)
    charts["Estado de ánimo"] = build_chart("mood", "Estado de ánimo", "Estado", color=SECONDARY)
    charts["Temperatura corporal"] = build_chart("body_temperature", "Temperatura corporal", "°C", color=PRIMARY)

    charts = {k: v for k, v in charts.items() if v is not None}

    return charts