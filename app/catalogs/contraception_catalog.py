from .base import BaseCatalog

class ContraceptionCatalog(BaseCatalog):
    MAP = {
        "pill": "Píldora",
        "iud": "DIU",
        "implant": "Implante",
        "injection": "Inyección",
        "condom": "Condón",
        "none": "Ninguno"
    }