import google.genai as genai
import os
import json
import re

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def analyze_daily_message(message: str):
    prompt = f"""
You are a health assistant specialized in menstrual tracking.

Analyze the user message and extract structured data.

Return ONLY a valid JSON object.

Fields:

intent: one of ["log_symptoms", "start_period", "end_period"]

stress: integer (0-10)
anxiety: integer (0-10)
mood: integer (0-10)
cramps: integer (0-10)
cravings: 0 or 1

symptoms: array of strings (e.g. ["cramps", "headache", "fatigue"])

Rules:

- "me bajó", "empezó mi periodo" → intent = "start_period"
- "terminó mi periodo" → intent = "end_period"
- Symptoms must be normalized to simple English words
- DO NOT include events inside symptoms
- If something is not mentioned, omit it


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
        json_match = re.search(r'\{.*\}', text, re.DOTALL)

        if not json_match:
            return {"error": "No JSON found in response"}

        json_str = json_match.group()
        return json.loads(json_str)
    except Exception as e:
        return {"error": str(e)}