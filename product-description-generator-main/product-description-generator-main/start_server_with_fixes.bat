@echo off
echo Starting FastAPI server with enhanced logging...
echo.

REM Set environment variable to ensure Python output is not buffered
set PYTHONUNBUFFERED=1

REM Change to the directory where this batch file is located
cd /d %~dp0

REM Create necessary directories if they don't exist
if not exist "static" mkdir static
if not exist "generated_images" mkdir generated_images
if not exist "generated_audio" mkdir generated_audio

REM Create symbolic links if they don't exist
if not exist "static\generated_images" (
    echo Creating symbolic link for static\generated_images...
    mklink /J "static\generated_images" "generated_images"
)

if not exist "static\generated_audio" (
    echo Creating symbolic link for static\generated_audio...
    mklink /J "static\generated_audio" "generated_audio"
)

REM Start the FastAPI server
echo Starting FastAPI server...
python -m uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000

echo.
pause
