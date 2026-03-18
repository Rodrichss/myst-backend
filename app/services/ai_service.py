import google.genai as genai
import os
import json
import re

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def analyze_daily_message(message: str):
    prompt = f"""
You are a health assistant.

Extract symptoms and health indicators from the user's message.

Return ONLY a JSON object with these possible fields:

stress (0-10)
anxiety (0-10)
mood (0-10)
cramps (0-10)
cravings (0 or 1)
symptoms (string)

If something is not mentioned, do not include it.

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