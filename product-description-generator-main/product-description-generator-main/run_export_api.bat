@echo off
echo Starting the Product Generator API...

REM Create directories for generated content if they don't exist
if not exist "generated_images" (
    mkdir "generated_images"
    echo Created generated_images directory
)

if not exist "generated_gifs" (
    mkdir "generated_gifs"
    echo Created generated_gifs directory
)

echo.
echo Starting FastAPI server...
python export_api.py

echo.
echo API will be available at: http://localhost:8000
echo.
echo To stop the server, press Ctrl+C in this window.
