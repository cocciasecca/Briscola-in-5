# Files to upload to the fork

Copy this folder over the root of the original repository and allow replacement
of only `README.md` and `pyproject.toml`.

## Original files intentionally modified

- `README.md`: documents the optional LAN interface.
- `pyproject.toml`: adds FastAPI/Uvicorn, the `briscola5-web` command, and static package data.

## Original source code left unchanged

No file under these existing directories is replaced:

- `src/briscola5/domain/`
- `src/briscola5/application/`
- `src/briscola5/bots/`
- `src/briscola5/cli/`
- existing original tests

All gameplay differences required by the web version are isolated in
`src/briscola5/web/engine/`.
