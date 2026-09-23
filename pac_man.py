import uvicorn

PORT = 5000
URL = f"http://localhost:{PORT}"


def main() -> None:
    uvicorn.run("backend.server:app", port=PORT, log_level="error")


if __name__ == "__main__":
    main()
