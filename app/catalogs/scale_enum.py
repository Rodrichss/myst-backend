from app.utils.base_normalizer import normalize_text

class ScaleEnum:
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4

    MAP = {
        0: "Ninguno",
        1: "Leve",
        2: "Moderado",
        3: "Alto",
        4: "Muy alto"
    }

    REVERSE_MAP = {
        normalize_text(v): k for k, v in MAP.items()
    }