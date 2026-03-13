import subprocess
import sys
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard = os.path.join(script_dir, "dashboard.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard])