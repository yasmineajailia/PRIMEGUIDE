Set-Location -Path "d:\PI\product-description-generator-main\product-description-generator-main"
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8001 --reload
