from .base import BaseCatalog

class SymptomsCatalog(BaseCatalog):
    MAP = {
        "headache": "Dolor de cabeza",
        "sore_throat": "Dolor de garganta",
        "muscle_aches": "Dolor muscular",
        "back_pain": "Dolor de espalda",
        "shortness_of_breath": "Falta de aliento",
        "fatigue": "Fatiga",
        "insomnia": "Insomnio",
        "fever": "Fiebre",
        "cough": "Tos",
        "bloating": "Hinchazón",
        "diarrhea": "Diarrea",
        "constipation": "Estreñimiento",
        "loss_of_taste_or_smell": "Pérdida de sabor o olfato",
        "nausea_or_vomiting": "Náusea o vómito"
    }