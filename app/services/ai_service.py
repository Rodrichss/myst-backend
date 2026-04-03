import google.genai as genai
import os
import json
import re
from datetime import date

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def analyze_daily_message(message: str):

    today = date.today().isoformat()  # contexto de fecha real para el modelo

    prompt = f"""
You are a health assistant specialized in menstrual tracking.
Today's date is {today}.

Analyze the user message and extract structured data.
Return ONLY a valid JSON object.

Fields to extract:

- intent: one of ["log_symptoms", "start_period", "end_period"]
- date: ISO format (YYYY-MM-DD). Use today ({today}) if no date is mentioned.
  IMPORTANT: never return a future date. If the mentioned date would be in the future,
  use the same day/month from the previous year.
- stress: integer 0-10
- anxiety: integer 0-10
- mood: integer 0-10
- cramps: integer 0-10
- cravings: 0 or 1
- symptoms: array of strings (e.g. ["headache", "fatigue", "bloating"])
 
Rules for intent:
- "me bajó", "empezó mi periodo", "me llegó", "inicio de ciclo" → intent = "start_period"
- "terminó mi periodo", "se fue", "acabó mi regla", "fin de ciclo" → intent = "end_period"
- anything else → intent = "log_symptoms"

Rules for dates:
- "hoy" → {today}
- "ayer" → subtract 1 day from {today}
- "el lunes", "el martes", etc. → find the most recent past occurrence of that weekday
- "15 de noviembre", "el 3 de marzo" → use the current year {date.today().year},
  but if that date is in the future, use {date.today().year - 1} instead
- Always output date as YYYY-MM-DD
 
Rules for symptoms:
- Normalize to simple English words
- Do NOT include events (e.g. "period started") in symptoms
 
If a field is not mentioned, omit it from the JSON entirely.


User message:
{message}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
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