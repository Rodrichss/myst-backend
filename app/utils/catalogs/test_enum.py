from app.utils.base_normalizer import normalize_text
class TestEnum:
    NEGATIVE = 0
    POSITIVE = 1
    INCONCLUSIVE = 2
    NOT_TAKEN = 3

    MAP = {
        0: "Negativo",
        1: "Positivo",
        2: "Indeterminado",
        3: "No realizada"
    }

    REVERSE_MAP = {
        normalize_text(v): k for k, v in MAP.items()
    }