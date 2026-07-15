from __future__ import annotations

import argparse
import webbrowser

import uvicorn

from briscola5.web.app import local_ip, start_discovery


def main() -> None:
    parser = argparse.ArgumentParser(description="Avvia Briscola in 5 sulla rete locale")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    lan_url = f"http://{local_ip()}:{args.port}"
    print("\nBriscola in 5 LAN")
    print(f"Sul PC host: http://127.0.0.1:{args.port}")
    print(f"Sugli altri dispositivi: {lan_url}\n")
    start_discovery(args.port)
    if not args.no_browser:
        webbrowser.open(f"http://127.0.0.1:{args.port}")
    uvicorn.run("briscola5.web.app:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
