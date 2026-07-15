# LAN integration notes

## Design goal

The LAN feature is implemented as an optional extension without changing the
existing game engine, bots, CLI, or their tests.

## Isolation strategy

`src/briscola5/web/engine/` contains the web-specific adapter used by the
browser version. It preserves the original packages while supporting:

- Neapolitan card names and image identifiers;
- immediate normal play after the auction and call;
- browser-safe state serialization;
- bot timing and completed-trick animation.

This deliberate isolation avoids merge conflicts with future upstream changes.
The original terminal game remains available and behaves exactly as before.

## Transport and privacy

FastAPI exposes the lobby and player actions. WebSocket connections receive
viewer-specific snapshots. A client receives only its own cards; opponents'
actual hands remain on the host.

Reconnect tokens are generated server-side and stored only by the owning
browser. If a human disconnects, the game pauses until reconnection or host
replacement with a bot.

## Original files changed

Only two existing repository files are replaced:

- `pyproject.toml` for web dependencies, package data, and launcher command;
- `README.md` for integrated usage documentation.

All other files in this patch are additions.
