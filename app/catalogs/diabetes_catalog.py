from .base import BaseCatalog

class DiabetesCatalog(BaseCatalog):
    MAP = {
        "none": "Ninguna",
        "type_1": "Tipo 1",
        "type_2": "Tipo 2",
        "gestational": "Gestacional",
        "prediabetes": "Prediabetes"
    }