from .base import BaseCatalog

class ActivityCatalog(BaseCatalog):
    MAP = {
        "none": "Ninguna",
        "reading": "Lectura",
        "self_care": "Cuidado personal",
        "rest": "Descanso",
        "dancing": "Baile",
        "entertainment": "Entretenimiento",
        "painting": "Pintar",
        "cooking": "Cocinar",
        "gardening": "Jardinería",
        "writing": "Escribir",
        "other": "Otro",
    }