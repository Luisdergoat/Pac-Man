#imports die sachen die gebraucht werden um das programm mit python3 zu starten.
import os
import time
from pathlib import Path
import subprocess
import platform

VENV_NAME = "venv"
BACKEND_DIR = Path(__file__).parent / "backend"
Port = 5000
URL = f"http://localhost:{Port}"
TERMINAL_INPUT = f"cd {BACKEND_DIR} && rm -rf {VENV_NAME} && uv venv {VENV_NAME} --python 3.12 --seed && source {VENV_NAME}/bin/activate &&{VENV_NAME}/bin/pip install -r requirements.txt && {VENV_NAME}/bin/uvicorn server:app --reload --port {Port}"
SCRIPT = f'tell application "Terminal" to do script "{TERMINAL_INPUT}"'
PLATFORM = platform.system()


def main():
    if PLATFORM == "Darwin":
        subprocess.run(["osascript", "-e", SCRIPT])
        time.sleep(10)  # make sure the server is up and running
        subprocess.run(["open", "-a", "Google Chrome", URL])
    else:
        subprocess.run(["gnome-terminal", "--", "bash", "-c", TERMINAL_INPUT])
        time.sleep(10)  # make sure the server is up and running
        subprocess.run(["open", "-a", "Google Chrome", URL])


if __name__ == "__main__":
    main()
