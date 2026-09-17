Set-Location -Path "d:\PI\product-description-generator-main"
python -m uvicorn image_description_service:app --host 127.0.0.1 --port 8001 --reload
