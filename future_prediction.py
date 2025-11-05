import os
import re
import json
import time
from datetime import datetime
from google.api_core.exceptions import ResourceExhausted
import google.generativeai as genai




API_KEY = os.getenv("GEMINI_API_KEY") # Replace with your real key
MODEL = "models/gemini-2.0-flash-lite"  # ✅ Confirmed working model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL)


# === Utility: Fetch news summary (placeholder) ===
def fetch_news_summary(symbol, company_name):
    """
    Stub for recent news collection — replace later with a real API.
    """
    return f"No major recent news available for {company_name} ({symbol})."


# === Helper: Extract JSON from AI output ===
def extract_json_from_text(text: str):
    """
    Extracts the first valid JSON block from Gemini output.
    Cleans code fences and other text wrappers.
    """
    if not text:
        return None

    cleaned = re.sub(r"```(?:json|txt)?\n?", "", text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    cleaned = re.sub(r"^\s*json\s*", "", cleaned, flags=re.IGNORECASE)

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            try:
                fixed = re.sub(r",\s*}", "}", match.group(0))
                fixed = re.sub(r",\s*\]", "]", fixed)
                return json.loads(fixed)
            except Exception:
                return None
    try:
        # fallback: parse "key: value" style lines
        lines = [ln.strip() for ln in cleaned.splitlines() if ":" in ln]
        if not lines:
            return None
        out = {}
        for ln in lines:
            k, v = ln.split(":", 1)
            out[k.strip().strip('"').strip("'")] = v.strip().strip('"').strip("'")
        return out
    except Exception:
        return None


# === Core AI Forecast Function ===
def get_ai_forecast(company_name, signal_summary, news_summary):
    """
    Calls Gemini to predict the next 6–12 month stock outlook.
    Returns parsed JSON dict.
    """
    prompt = f"""
You are a senior equity research analyst.

Using the given company's technical summary and news, predict its **stock price trend and expected % change for both the next 6 months and the next 12 months**.

Company: {company_name}
Technical Summary: {signal_summary}
Recent News Summary: {news_summary}

Respond strictly in VALID JSON format (no extra text) using:
{{
  "prediction": "Bullish" | "Neutral" | "Bearish",
  "expected_change_6m": "<approx % change or range>",
  "expected_change_1y": "<approx % change or range>",
  "confidence": "High" | "Medium" | "Low",
  "reasoning": "<3–4 concise sentences explaining the trend>"
}}

Example:
{{
  "prediction": "Bullish",
  "expected_change_6m": "+8% to +15%",
  "expected_change_1y": "+15% to +25%",
  "confidence": "Medium",
  "reasoning": "Strong fundamentals, improving margins, and positive sector outlook support upside momentum over the next year."
}}
"""

    retries = 4
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip() if getattr(response, "text", None) else ""
            parsed = extract_json_from_text(text)
            if parsed:
                # Normalize keys and ensure consistent structure
                out = {
                    "prediction": parsed.get("prediction", "Neutral"),
                    "expected_change_6m": parsed.get("expected_change_6m") or parsed.get("expected_change") or "0%",
                    "expected_change_1y": parsed.get("expected_change_1y") or "0%",
                    "confidence": parsed.get("confidence", "Medium"),
                    "reasoning": (parsed.get("reasoning") or "").strip(),
                }
                return out
            elif text:
                # Fallback if model returns descriptive text
                return {
                    "prediction": "Neutral",
                    "expected_change_6m": "0%",
                    "expected_change_1y": "0%",
                    "confidence": "Low",
                    "reasoning": text[:800],
                }
            else:
                raise ValueError("Empty model response")

        except ResourceExhausted as e:
            wait_time = (attempt + 1) * 10
            print(f"⚠️ Rate limit hit for {company_name}. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            if attempt == retries - 1:
                print(f"⚠️ Gemini call failed for {company_name}: {e}")
                return {
                    "prediction": "Neutral",
                    "expected_change_6m": "0%",
                    "expected_change_1y": "0%",
                    "confidence": "Low",
                    "reasoning": f"Error: {str(e)}",
                }
            else:
                print(f"Retrying {company_name} after error: {e}")
                time.sleep(5 + attempt * 5)

    return {
        "prediction": "Neutral",
        "expected_change_6m": "0%",
        "expected_change_1y": "0%",
        "confidence": "Low",
        "reasoning": "Gemini did not return a usable forecast after retries.",
    }


# === Enrichment Process ===
def enrich_signals(input_file="signals.json", output_file="signals_enriched.json"):
    """
    Enriches stock signals with AI-based forecasts and saves to file.
    """
    if not os.path.exists(input_file):
        print(f"❌ Input file '{input_file}' not found. Run signal_analysis.py first.")
        return

    with open(input_file, "r") as f:
        data = json.load(f)

    stocks = data.get("stocks", {})
    print(f"🔍 Generating AI forecasts for {len(stocks)} stocks...")

    for name, analysis in stocks.items():
        basic = analysis.get("basic_data", {})
        signal_summary = (
            f"Signal: {analysis.get('signal', 'N/A')}, "
            f"Weekly Change: {basic.get('weekly_change', 'N/A')}%, "
            f"RSI: {analysis.get('technical_indicators', {}).get('rsi', 'N/A')}, "
            f"Score: {analysis.get('technical_indicators', {}).get('score', 'N/A')}"
        )

        news_summary = fetch_news_summary(name, name)
        forecast = get_ai_forecast(name, signal_summary, news_summary)
        analysis["future_outlook"] = forecast

        # small delay to prevent rate limits
        time.sleep(3)

    data["forecast_time"] = datetime.utcnow().isoformat()

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Enriched file saved as '{output_file}' with AI-based forecasts.")


# === Entry Point ===
if __name__ == "__main__":
    enrich_signals()
