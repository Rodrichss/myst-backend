from .base import BaseCatalog

class MedicationCatalog(BaseCatalog):
    MAP = {
        "analgesics": "Analgésicos",
        "antibiotics": "Antibióticos",
        "antidepressants": "Antidepresivos",
        "hormonal": "Terapia hormonal"
    }