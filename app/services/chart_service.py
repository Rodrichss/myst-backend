import matplotlib.pyplot as plt
import tempfile

def stress_chart(cycles):
    dates = []
    stress_values = []

    for cycle in cycles:
        for log in cycle.daily_logs:
            if log.stress is not None:
                dates.append(log.date)
                stress_values.append(log.stress)

    # Ordenar por fecha (muy importante)
    combined = sorted(zip(dates, stress_values), key=lambda x: x[0])
    dates, stress_values = zip(*combined) if combined else ([], [])

    plt.figure()
    plt.plot(dates, stress_values)
    plt.title("Nivel de estrés diario")
    plt.xlabel("Fecha")
    plt.ylabel("Estrés")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp.name)
    plt.close()

    return tmp.name