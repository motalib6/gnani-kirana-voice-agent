@echo off
REM Windows one-command run: double-click this file.
REM Opens the linked app at http://127.0.0.1:8000/ (frontend + backend together).
REM Keep this window open while you test. Press CTRL+C to stop.
cd /d %~dp0backend
uvicorn app.main:app --reload --port 8000
pause
