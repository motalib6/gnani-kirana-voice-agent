#!/bin/bash
# Linux / macOS one-command run.
# Then open http://127.0.0.1:8000/ (frontend + backend together).
cd "$(dirname "$0")/backend" || exit 1
uvicorn app.main:app --reload --port 8000
