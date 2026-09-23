import uvicorn
import webbrowser
PORT = 5000
URL = f"http://localhost:{PORT}"


def main() -> None:
    webbrowser.open(URL)
    uvicorn.run("src.server:app", port=PORT, log_level="error")


if __name__ == "__main__":
    main()
