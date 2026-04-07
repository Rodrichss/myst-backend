from .base import BaseCatalog

class SexBiologyCatalog(BaseCatalog):
    # Solo opciones científicas/biológicas
    MAP = {
        "femenine": "Femenino",
        "masculine": "Masculino",
    }

class SexLegallyCatalog(SexBiologyCatalog):
    # Hereda de biología y añade opciones legales
    MAP = SexBiologyCatalog.MAP.copy()
    MAP.update({
        "non_binary": "No binario",
        "prefer_not_to_say": "Prefiero no decirlo" # Opcional, común en legal
    })