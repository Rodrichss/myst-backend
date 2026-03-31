from app.utils.base_normalizer import normalize_text
class FlowEnum:
    MAP = {
        0: "Nulo",
        1: "Ligero",
        2: "Medio",
        3: "Abundante",
        4: "Goteo"
    }

    REVERSE_MAP = {
        normalize_text(v): k for k, v in MAP.items()
    }