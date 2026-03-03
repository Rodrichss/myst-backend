import matplotlib.pyplot as plt
import tempfile

def stress_chart(cycles):
    dates = [c.period_start_date for c in cycles if c.stress]
    stress = [c.stress for c in cycles if c.stress]

    plt.figure()
    plt.plot(dates, stress)
    plt.title("Nivel de estrés por ciclo")
    plt.xlabel("Fecha")
    plt.ylabel("Estrés")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp.name)
    plt.close()

    return tmp.name