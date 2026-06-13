import time
import json
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

def categorize_transactions_batch(transactions_data: list) -> tuple[dict, str]:
    if not client:
        return None, "Gemini API key is missing."

    prompt = f"""
    You are a financial categorization AI. Categorize the following JSON list of transactions.
    Allowed categories ONLY: Food, Shopping, Travel, Transport, Utilities, Cash Withdrawal, Entertainment, Other.
    
    Transactions:
    {json.dumps(transactions_data, indent=2)}
    
    Return ONLY a valid JSON object where the keys are the IDs and the values are the assigned categories.
    Do not include any markdown formatting. Example: {{"15": "Food", "16": "Shopping"}}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Upgraded to the active 2026 model
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            response_text = response.text.strip()
            
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
                
            return json.loads(response_text), response.text
        except Exception as e:
            if attempt == max_retries - 1:
                return None, str(e)
            time.sleep(2 * (2 ** attempt))
    return None, "Failed to communicate with LLM."


def generate_narrative_summary(stats: dict) -> dict:
    if not client:
        return None

    prompt = f"""
    You are an expert financial risk analyst. Analyze these exact transaction statistics and generate a final JSON summary report.

    Statistics:
    {json.dumps(stats, indent=2)}

    Return EXACTLY this JSON structure, filling in the narrative and risk_level based on the data:
    {{
        "total_spend_inr": {stats['total_spend_inr']},
        "total_spend_usd": {stats['total_spend_usd']},
        "top_merchants": {json.dumps(stats['top_merchants'])},
        "anomaly_count": {stats['anomaly_count']},
        "narrative": "Write a 2-3 sentence professional summary of the user's spending behavior and any potential risks highlighted by the anomalies.",
        "risk_level": "low, medium, or high"
    }}
    Do not include any markdown formatting like ```json. Return ONLY the raw JSON object.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Upgraded to the active 2026 model
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            response_text = response.text.strip()
            
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
                
            return json.loads(response_text)
        except Exception as e:
            print(f"Summary Generation failed (Attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 * (2 ** attempt))
    return None