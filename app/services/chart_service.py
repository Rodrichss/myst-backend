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
        labels = [textwrap.fill(label, 12) for label in enum.MAP.values()]
        plt.yticks(keys, labels)

    def build_chart(field, title, ylabel, color = PRIMARY):
        dates = []
        values = []

        for log in logs:
            val = getattr(log, field, None)
            if val is not None:
                dates.append(log.date)
                values.append(val)

        if not dates:
            return None

        plt.figure()
        plt.plot(dates, values, marker="o", color=color)

        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        plt.gcf().autofmt_xdate()

        plt.title(title)
        plt.xlabel("Fecha")
        plt.ylabel(textwrap.fill(ylabel, 15))

        apply_enum_labels(field)

        plt.xticks(rotation=45)
        plt.tight_layout()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(tmp.name)
        plt.close()

        return tmp.name

    charts["Estrés"] = build_chart("stress", "Estrés diario", "Nivel", PRIMARY)
    charts["Ansiedad"] = build_chart("anxiety", "Ansiedad diaria", "Nivel", SECONDARY)
    charts["Cólicos"] = build_chart("cramps", "Cólicos", "Intensidad", PRIMARY)
    charts["Ánimo"] = build_chart("mood", "Estado de ánimo", "Estado", SECONDARY)

    return {k: v for k, v in charts.items() if v}