from app.utils.base_normalizer import normalize_text
class DischargeEnum:
    MAP = {
        0: "No sé",
        1: "Seco",
        2: "Pegajoso",
        3: "Cremoso",
        4: "Acuoso",
        5: "Clara de huevo",
        6: "Anormal",
        7: "Ninguno"
    }

    REVERSE_MAP = {
        normalize_text(v): k for k, v in MAP.items()
    }