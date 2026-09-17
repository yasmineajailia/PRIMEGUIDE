cd "d:\PI\product-description-generator-main\product-description-generator-main"
# Use uvicorn to run the fastapi_app.py file
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000 --reload