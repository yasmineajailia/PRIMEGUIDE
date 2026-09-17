import logging
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_api.log")
    ]
)
logger = logging.getLogger("test-api")

# Initialize FastAPI app
app = FastAPI(title="Test API")

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("generated_images", exist_ok=True)

# Create symbolic links if needed
if not os.path.exists("static/generated_images"):
    logger.info("Creating symbolic link for static/generated_images")
    if os.name == 'nt':  # Windows
        cmd = f'mklink /J "{os.path.abspath("static/generated_images")}" "{os.path.abspath("generated_images")}"'
        logger.info(f"Running command: {cmd}")
        os.system(cmd)
    else:  # Unix
        os.symlink(os.path.abspath("generated_images"), os.path.abspath("static/generated_images"))

# Mount static directories
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")

class TestResponse(BaseModel):
    success: bool
    message: str

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Test API is running"}

@app.get("/test-images")
async def test_images():
    logger.info("Test images endpoint called")
    
    # Create a test file in generated_images directory
    test_file_path = "generated_images/test.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file")
    
    # Create URL paths for both direct and static access
    direct_url = f"/generated_images/test.txt"
    static_url = f"/static/generated_images/test.txt"
    
    logger.info(f"Created test file at {test_file_path}")
    logger.info(f"Direct URL: {direct_url}")
    logger.info(f"Static URL: {static_url}")
    
    return {
        "success": True,
        "message": "Test file created",
        "direct_url": direct_url,
        "static_url": static_url
    }

if __name__ == "__main__":
    logger.info("Starting test API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
