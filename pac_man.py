#imports die sachen die gebraucht werden um das programm mit python3 zu starten.
import os
from pathlib import Path
import subprocess
import platform

VENV_NAME = "venv"
BACKEND_DIR = Path(__file__).parent / "backend"
Port = 5000
URL = f"http://localhost:{Port}"
TERMINAL_INPUT = f"cd {BACKEND_DIR} && source {VENV_NAME}/bin/activate && uvicorn server:app --reload --port {Port}"
SCRIPT = f'tell application "Terminal" to do script "{TERMINAL_INPUT}"'
PLATFORM = platform.system()


def main():
    if PLATFORM == "Darwin":
        subprocess.run(["osascript", "-e", SCRIPT])
    else:
        subprocess.run(["gnome-terminal", "--", "bash", "-c", TERMINAL_INPUT])


if __name__ == "__main__":
    main()
