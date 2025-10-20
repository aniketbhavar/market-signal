import subprocess
import sys
import datetime
import json
import os

def run_pipeline():
    print(f"\n🚀 Running pipeline at {datetime.datetime.now()}")

    python_exec = sys.executable

    # Step 1: Run Data Ingestion
    subprocess.run([python_exec, "Data_Ingestion.py"], check=True)

    # Step 2: Run Signal Analysis
    subprocess.run([python_exec, "signal_analysis.py"], check=True)

    # Step 3: ✅ Update metadata in both JSONs (without overwriting)
    now = datetime.datetime.now().isoformat()

    # --- Update market_data.json ---
    try:
        with open("market_data.json", "r") as f:
            market_data = json.load(f)
    except FileNotFoundError:
        market_data = {}

    market_data["last_run"] = now
    with open("market_data.json", "w") as f:
        json.dump(market_data, f, indent=2)

    # --- Update signals.json ---
    try:
        with open("signals.json", "r") as f:
            signals_data = json.load(f)
    except FileNotFoundError:
        signals_data = {}

    signals_data["last_run"] = now
    with open("signals.json", "w") as f:
        json.dump(signals_data, f, indent=2)

    print("✅ Pipeline completed successfully with updated metadata!\n")

if __name__ == "__main__":
    run_pipeline()
