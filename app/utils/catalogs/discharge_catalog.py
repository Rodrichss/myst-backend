from .base import BaseCatalog

class DischargeCatalog(BaseCatalog):
    MAP = {
        "dry": "Seco",
        "sticky": "Pegajoso",
        "creamy": "Cremoso",
        "watery": "Acuoso",
        "egg_white": "Clara de huevo",
        "abnormal": "Anormal",
        "none": "Ninguno"
    }