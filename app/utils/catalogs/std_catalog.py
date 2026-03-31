from .base import BaseCatalog

class STDCatalog(BaseCatalog):
    MAP = {
        "none": "Ninguna",
        "hpv": "VPH",
        "chlamydia": "Clamidia",
        "gonorrhea": "Gonorrea",
        "herpes": "Herpes",
        "syphilis": "Sífilis",
        "hiv": "VIH",
        "other": "Otra"
    }