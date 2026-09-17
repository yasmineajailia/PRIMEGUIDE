@echo off
echo Stopping any running FastAPI server...
taskkill /f /im python.exe /t 2>nul
timeout /t 1 /nobreak > nul

echo Creating necessary directories...
mkdir "d:\PI\product-description-generator-main\product-description-generator-main\static" 2>nul
mkdir "d:\PI\product-description-generator-main\product-description-generator-main\static\generated_images" 2>nul
mkdir "d:\PI\product-description-generator-main\product-description-generator-main\static\generated_audio" 2>nul

echo Starting FastAPI server with enhanced logging...
cd /d "d:\PI\product-description-generator-main\product-description-generator-main"
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 --reload --log-level debug
