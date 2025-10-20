import subprocess
import sys
import datetime
import json

def run_pipeline():
    print(f"\n🚀 Running pipeline at {datetime.datetime.now()}")

    python_exec = sys.executable

    subprocess.run([python_exec, "Data_Ingestion.py"], check=True)
    subprocess.run([python_exec, "signal_analysis.py"], check=True)

    # Update JSON files to force commit detection
    now = datetime.datetime.now().isoformat()
    with open("signals.json", "w") as f:
        json.dump({"last_run": now}, f, indent=2)
    with open("market_data.json", "w") as f:
        json.dump({"last_run": now}, f, indent=2)

    print("✅ Files updated & pipeline completed!\n")

if __name__ == "__main__":
    run_pipeline()
