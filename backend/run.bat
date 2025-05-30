@echo off

REM Run the FastAPI app with uvicorn on port 3000
uvicorn main:app --host 0.0.0.0 --port 3000 --reload

pause
