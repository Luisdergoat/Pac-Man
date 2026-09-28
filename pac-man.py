import uvicorn
from src.server import create_app
import sys
PORT = 5000
URL = f"http://localhost:{PORT}"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 pac_man.py <config.json>")
        return

    app = create_app(sys.argv[1], URL)
    uvicorn.run(app, port=PORT, log_level="error")


if __name__ == "__main__":
    main()
