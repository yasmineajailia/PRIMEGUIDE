@echo off
cd /d "d:\PI\product-description-generator-main\product-description-generator-main"
echo Starting FastAPI server...
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 --reload
