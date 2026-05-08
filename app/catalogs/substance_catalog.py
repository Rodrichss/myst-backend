from .base import BaseCatalog

class SubstanceCatalog(BaseCatalog):
    MAP = {
        "none": "Ninguna",
        "alcohol": "Alcohol",
        "caffeine": "Cafeína",
        "nicotine": "Nicotina",
        "cannabis": "Marihuana",
        "other": "Otra"
    }