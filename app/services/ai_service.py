import google.genai as genai
import os
import json
import re
from datetime import date, timedelta

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ── System prompt estático (candidato a cache) ─────────────────────────────────
# Se define una sola vez. Gemini 2.5 flash-lite soporta implicit caching:
# si el prefijo del prompt es idéntico entre requests, se cachea automáticamente.
_SYSTEM_PROMPT = """You are a menstrual health assistant. Extract structured data AND provide empathetic support.
Return ONLY a valid JSON object — no markdown, no backticks, no explanation.

STRUCTURE:
Return a JSON with three main keys:
1. "data": {
    - All extracted fields go here.
    - All JSON keys must be lowercase (intent, date, stress, etc.)
    - Omit any field not mentioned by the user.

    INTENT (required):
    - start_period: "me bajó", "empezó mi periodo", "me llegó", "inicio de ciclo", "me vino"
    - end_period: "terminó mi periodo", "se fue", "acabó mi regla", "fin de ciclo"
    - log_symptoms: anything else
    - If intent is start_period, always include menstrual_flow (minimum 1) unless user says no bleeding

    DATE RULES:
    - "hoy" → today | "ayer" → today-1 | "antier" → today-2
    - weekday name → most recent past occurrence
    - "15 de noviembre" → use current year; if future, use previous year
    - Never return a future date
    - Format: YYYY-MM-DD

    FIELDS and valid values:
    menstrual_flow: 0=Nulo 1=Ligero 2=Medio 3=Abundante 4=Goteo
    mood: 1=Triste 2=Enojada 3=Neutral 4=Feliz 5=MuyFeliz 6=CambiosDeHumor
    stress: 0=Ninguno 1=Leve 2=Moderado 3=Alto 4=MuyAlto
    anxiety: 0=Ninguno 1=Leve 2=Moderado 3=Alto 4=MuyAlto
    cramps: 0=Ninguno 1=Leve 2=Moderado 3=Alto 4=MuyAlto
    cravings: 1=Dulce 2=Salado 3=Chocolate 4=Carbohidratos 5=Chatarra 6=Saludable 7=Picante 8=Ninguno
    vaginal_discharge: 1=Seco 2=Pegajoso 3=Cremoso 4=Acuoso 5=ClaraHuevo 6=Anormal 7=Ninguno
    pregnancy_test: 0=Negativo 1=Positivo 2=Indeterminado 3=NoRealizada
    ovulation_test: 0=Negativo 1=Positivo 2=Indeterminado 3=NoRealizada

    symptoms (array, use only these keys):
    headache sore_throat muscle_aches back_pain shortness_of_breath
    fatigue insomnia fever cough bloating diarrhea constipation
    loss_of_taste_or_smell nausea_or_vomiting

    exercise (string, one key):
    running swimming cycling hiking yoga weightlifting boxing walking other

    hobbies_activities (string, one or more keys comma-separated):
    reading self_care rest dancing entertainment painting cooking gardening writing other

    anticonceptive_type (string, one key):
    pill iud implant injection condom none

    Other numeric fields (use realistic values):
    weight: kg (float) | height: cm (float) | heart_rate: bpm (int)
    water_consumption: liters (float) | sleep_time: HH:MM | exercise_time: HH:MM
    sexual_penetration: true/false | anticonceptive_use: true/false
}
2. "is_red_flag": boolean (true if symptoms like hemorrhaging, fainting, or extreme pain are detected)
3. "response": "A short, empathetic message in SPANISH. Include a self-care tip, a contextual question about stress/lifestyle, or a medical suggestion if is_red_flag is true. NEVER give a medical diagnosis."
"""


def analyze_daily_message(message: str) -> dict:
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()

    # User prompt: solo fecha + mensaje (corto, varía por request)
    user_prompt = (
        f"Today: {today.isoformat()} | Yesterday: {yesterday}\n"
        f"User message: {message}"
    )

    full_prompt = f"{_SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt,
            config={
                "response_mime_type": "application/json", # Esto fuerza a Gemini a dar JSON puro
            }
        )
        return parse_response(response)
    except Exception as e:
        return {"error": str(e)}

def parse_response(response):
    try:
        text = response.text

        # Quitar bloques de código markdown si el modelo los devuelve igual
        text = re.sub(r"```(?:json)?", "", text).strip()

        json_match = re.search(r'\{.*\}', text, re.DOTALL)

        if not json_match:
            return {"error": "No JSON found in response"}

        json_str = json_match.group()
        return json.loads(json_str)
    except Exception as e:
        return {"error": str(e)}