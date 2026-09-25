import uvicorn
from src.server import create_app
PORT = 5000
URL = f"http://localhost:{PORT}"


def main() -> None:
    app = create_app("config.json", URL)
    uvicorn.run(app, port=PORT, log_level="error")


if __name__ == "__main__":
    main()
