from __future__ import annotations

import asyncio
import socket
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from briscola5.web.manager import GameManager

# This module is intentionally thin: HTTP/WebSocket transport lives here,
# while game rules and multiplayer coordination remain in GameService/GameManager.
STATIC_DIR = Path(__file__).with_name("static")
app = FastAPI(title="Briscola in 5 LAN")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
manager = GameManager()


# Pydantic request models keep browser input validation at the API boundary.
class JoinRequest(BaseModel):
    name: str
    token: str | None = None


class TokenRequest(BaseModel):
    token: str


class BidRequest(TokenRequest):
    offer: int | None = None


class PlayRequest(TokenRequest):
    card_index: int


class CallRequest(TokenRequest):
    suit: str
    rank: str


class ReplaceRequest(TokenRequest):
    player_id: int


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/info")
def info() -> dict[str, Any]:
    return {"name": "Briscola in 5", "lan_ip": local_ip(), "port": 8000}


@app.post("/api/join")
async def join(request: JoinRequest) -> dict[str, Any]:
    async with manager.lock:
        try:
            player_id, token, is_host = manager.join(request.name, request.token)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        await manager.broadcast()
        return {"player_id": player_id, "token": token, "is_host": is_host}


@app.post("/api/start")
async def start(request: TokenRequest) -> dict[str, bool]:
    async with manager.lock:
        try:
            manager.start_game(request.token)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        await manager.broadcast()
    asyncio.create_task(manager.run_bots())
    return {"ok": True}


@app.post("/api/bid")
async def bid(request: BidRequest) -> dict[str, bool]:
    async with manager.lock:
        try:
            manager.bid(request.token, request.offer)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        await manager.broadcast()
    asyncio.create_task(manager.run_bots())
    return {"ok": True}


@app.post("/api/play")
async def play(request: PlayRequest) -> dict[str, bool]:
    async with manager.lock:
        try:
            manager.play(request.token, request.card_index)
        except (ValueError, IndexError) as exc:
            raise HTTPException(400, str(exc)) from exc
        await manager.broadcast()
    asyncio.create_task(manager.run_bots())
    return {"ok": True}


@app.post("/api/call")
async def make_call(request: CallRequest) -> dict[str, bool]:
    async with manager.lock:
        try:
            manager.call(request.token, request.suit, request.rank)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        await manager.broadcast()
    asyncio.create_task(manager.run_bots())
    return {"ok": True}


@app.post("/api/replace")
async def replace(request: ReplaceRequest) -> dict[str, bool]:
    async with manager.lock:
        try:
            manager.replace_with_bot(request.token, request.player_id)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        await manager.broadcast()
    asyncio.create_task(manager.run_bots())
    return {"ok": True}


@app.get("/api/state")
def state(token: str | None = None) -> dict[str, Any]:
    return manager.public_state(token)


# Each authenticated browser owns one WebSocket used only for server-to-client
# state updates. Player actions continue to use explicit HTTP endpoints.
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    await websocket.accept()
    seat = manager.seat_for_token(token)
    if seat is None:
        await websocket.close(code=4401)
        return
    seat.connected = True
    manager.websockets[token] = websocket
    manager._refresh_pause()
    await manager.broadcast()
    asyncio.create_task(manager.run_bots())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.websockets.pop(token, None)
        manager.disconnect(token)
        await manager.broadcast()


def local_ip() -> str:
    """Return the LAN-facing IPv4 address without sending application data."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def start_discovery(port: int = 8000) -> None:
    """Answer UDP discovery packets on the LAN; failure is harmless."""
    def worker() -> None:
        # UDP discovery is optional; manual IP entry remains the reliable fallback.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", 54545))
            while True:
                data, address = sock.recvfrom(128)
                if data == b"BRISCOLA5_DISCOVER":
                    sock.sendto(f"BRISCOLA5 http://{local_ip()}:{port}".encode(), address)
        except OSError:
            pass
        finally:
            sock.close()

    threading.Thread(target=worker, daemon=True).start()
