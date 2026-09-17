from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import uvicorn
from PIL import Image
from io import BytesIO
import base64
import requests
import json

# Create a simple FastAPI app that proxies requests to the main API
app = FastAPI(
    title="Image Description Service",
    description="Proxy service that forwards image description requests to the main API",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The main API URL
MAIN_API_URL = "http://127.0.0.1:8000"

@app.get("/")
async def root():
    """Root endpoint to check API status"""
    return {
        "status": "online",
        "message": "Image Description Service is running",
        "endpoints": {
            "POST /generate-description-from-image": "Generate a description from an uploaded image (proxies to main API's /upload-image)"
        }
    }

@app.post("/generate-description-from-image")
async def generate_description_from_image(image: UploadFile = File(...)):
    """Generate a product description from an uploaded image (proxies to /upload-image)"""
    try:
        # Read the uploaded image
        contents = await image.read()
        
        # Create a file object to send to the main API
        files = {'image': (image.filename, contents, image.content_type)}
        
        # Send the request to the main API's /upload-image endpoint
        response = requests.post(f"{MAIN_API_URL}/upload-image", files=files)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            # If there was an error, return the error response
            raise HTTPException(status_code=response.status_code, detail=response.text)
    
    except Exception as e:
        # Handle any errors
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# Run the application
if __name__ == "__main__":
    # Run on a different port than the main API
    uvicorn.run("image_description_service:app", host="127.0.0.1", port=8001, reload=True)
