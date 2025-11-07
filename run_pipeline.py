import subprocess
import sys
import datetime
import json
import os
from dotenv import load_dotenv
load_dotenv()
def run_pipeline():
    print(f"\n🚀 Running pipeline at {datetime.datetime.now()}")

    python_exec = sys.executable

    # Step 1: Run Data Ingestion
    subprocess.run([python_exec, "Data_Ingestion.py"], check=True)

    # Step 2: Run Signal Analysis
    subprocess.run([python_exec, "signal_analysis.py"], check=True)

    # Step 3: Run AI Future Prediction (Gemini)
    # -----------------------------------------------------
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Skipping future predictions.")
    else:
        env = os.environ.copy()
        env["GEMINI_API_KEY"] = api_key
        subprocess.run([python_exec, "future_prediction.py"], check=True, env=env)
    # -----------------------------------------------------

    # Step 4: ✅ Update metadata
    now = datetime.datetime.now().isoformat()

    for filename in ["market_data.json", "signals.json", "signals_enriched.json"]:
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        data["last_run"] = now
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    print("✅ Pipeline completed successfully with AI predictions and metadata!\n")


if __name__ == "__main__":
    run_pipeline()
