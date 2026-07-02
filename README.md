# Flashpoint

This is a public, sanitized copy of Flashpoint with private credentials removed. Use this repository to run the bot locally or as a starting point for deployment. Do NOT commit any `.env` or secrets.

## Quickstart (local)

1. Create and activate a Python virtual environment:

   PowerShell:
   ```powershell
   python -m venv .venv
   & .venv\Scripts\Activate.ps1
   ```

   macOS / Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (do not commit):

   - Create a local `.env` file in the `flashpoint-2` folder (or set env vars in your shell/CI).
   - Example variables:

     ```ini
     SE_EMAIL=you@example.com
     SE_PASSWORD=yourpassword
     SE_API_KEY=optional-api-key
     CHAT_ROOM_ID=25999
     SITE_NAME=stackoverflow
     ```

   - Keep `.env` out of source control. Use `secrets` or environment variables in CI.

4. Run the bot:

   ```bash
   python -m flashpoint
   ```

## Notes for the public copy

- `settings.py` has been sanitized to avoid requiring a private `.env` at import time and to remove personal admin IDs.
- Remove local artifacts before publishing: `.venv/`, `.env`, and `__pycache__/`.
- Add a `.env.example` with placeholder values and ensure your `.gitignore` excludes `.env` and virtual environments.

## Project layout

- `app/` - main scanning loop and runtime state
- `chat/` - chat connection, adapters, and command routing
- `brain/` - heuristics and detection logic
- `api/` - Stack API client management
- `utils/` - helpers and logging

If you want, I can add a `.env.example` file and a recommended `.gitignore` to this repository.
