import subprocess
import sys
import datetime

def run_pipeline():
    print(f"\n🚀 Running pipeline at {datetime.datetime.now()}")

    python_exec = sys.executable

    subprocess.run([python_exec, "Data_Ingestion.py"], check=True)
    subprocess.run([python_exec, "signal_analysis.py"], check=True)

    print("Pipeline completed!\n")

if __name__ == "__main__":
    run_pipeline()