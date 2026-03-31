from app.utils.base_normalizer import normalize_text
class MoodEnum:
    MAP =  {
        1: "Triste",
        2: "Enojada",
        3: "Neutral",
        4: "Feliz",
        5: "Muy feliz",
        6: "Cambios de humor"
    }

    REVERSE_MAP = {
        normalize_text(v): k for k, v in MAP.items()
    }