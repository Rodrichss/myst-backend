from app.utils.base_normalizer import normalize_text
class CravingsEnum:
    MAP = {
        1: "Dulce",
        2: "Salado",
        3: "Chocolate",
        4: "Carbohidratos",
        5: "Comida chatarra",
        6: "Comida saludable",
        7: "Picante",
        8: "Ninguno"
    }

    REVERSE_MAP = {
        normalize_text(v): k for k, v in MAP.items()
    }