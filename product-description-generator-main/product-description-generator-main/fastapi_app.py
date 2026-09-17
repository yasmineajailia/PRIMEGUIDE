from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import os
import sys
import traceback
import shutil
import logging
from typing import Optional, List, Dict, Any
import json
import uvicorn
from dotenv import load_dotenv
import google.generativeai as genai
import numpy as np
import pandas as pd
import tempfile
import uuid
from datetime import datetime
import time

# Add parent directory to path to import from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import generators
from generators.audio_generator import generate_audio, voice_descriptions
from generators.image_generator import generate_product_image, image_desc_generator
from generators.gif_generator import generate_gif_from_description

# Setup logging
from utils.logging_config import logger

# Load environment variables
load_dotenv()

# Setup Gemini API
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
# If the API key is not found in environment variables, try to read it directly from .env file
if not GEMINI_API_KEY:
    logger.warning("GOOGLE_API_KEY not found in environment variables, trying to read from .env file")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    logger.info(f"Looking for .env file at: {env_path}")
    if os.path.exists(env_path):
        logger.info(f".env file found at: {env_path}")
        try:
            with open(env_path, "r") as f:
                env_content = f.read()
                logger.info(f".env file content: {env_content}")
                for line in env_content.splitlines():
                    if line.startswith("GOOGLE_API_KEY="):
                        GEMINI_API_KEY = line.strip().split("=", 1)[1].strip()
                        logger.info(f"Found GOOGLE_API_KEY in .env file: {GEMINI_API_KEY[:5]}...")
                        break
        except Exception as e:
            logger.error(f"Error reading .env file: {str(e)}")
    else:
        logger.error(f".env file not found at: {env_path}")

if not GEMINI_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables or .env file")
    logger.error("Please create a .env file with your GOOGLE_API_KEY. See README.md for instructions.")
    GEMINI_API_KEY = None

# Initialize the Gemini model
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {str(e)}")
    logger.error(traceback.format_exc())

# Create directories if they don't exist
os.makedirs("generated_audio", exist_ok=True)
os.makedirs("generated_images", exist_ok=True)
os.makedirs("generated_gifs", exist_ok=True)
os.makedirs("temp_uploads", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Product AI Hub API",
    description="API for product description, image, and audio generation",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all necessary directories
os.makedirs("static", exist_ok=True)
os.makedirs("static/generated_images", exist_ok=True)
os.makedirs("static/generated_audio", exist_ok=True)
os.makedirs("static/generated_gifs", exist_ok=True)

# Mount static directory first (important for proper path resolution)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount direct access paths
app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")
app.mount("/generated_audio", StaticFiles(directory="generated_audio"), name="generated_audio")
app.mount("/generated_gifs", StaticFiles(directory="generated_gifs"), name="generated_gifs")

# Create symbolic links to the generated directories in static folder
# This is needed for accessing files via /static/generated_* paths
for directory in ["generated_images", "generated_audio", "generated_gifs"]:
    static_dir_path = f"static/{directory}"
    # Remove existing directory if it exists (to avoid conflicts)
    if os.path.exists(static_dir_path) and os.path.isdir(static_dir_path):
        try:
            # In Windows, we need to handle directory junctions differently
            if os.name == 'nt':
                import shutil
                shutil.rmtree(static_dir_path)
            else:
                os.rmdir(static_dir_path)
        except Exception as e:
            logger.warning(f"Could not remove existing directory {static_dir_path}: {e}")
    
    # Create symbolic link
    if not os.path.exists(static_dir_path):
        if os.name == 'nt':  # Windows
            os.system(f'mklink /J "{os.path.abspath(static_dir_path)}" "{os.path.abspath(directory)}"')
        else:  # Unix
            os.symlink(os.path.abspath(directory), os.path.abspath(static_dir_path))

# Define request models
class TextGenerationRequest(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    keywords: Optional[str] = Field("", description="Optional keywords to guide generation")
    tone: Optional[str] = Field("Professional", description="Tone of the description")
    model_type: Optional[str] = Field("default", description="Model type")

class ImageGenerationRequest(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    keywords: Optional[str] = Field("", description="Optional keywords to guide generation")
    image_style: Optional[str] = Field("product", description="Style of the image")
    image_size: Optional[str] = Field("512x512", description="Size of the image")

class AudioGenerationRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice_id: Optional[str] = Field("Aria", description="Voice ID to use")
    style: Optional[float] = Field(0.5, description="Style parameter (0.0-1.0)")

class GifGenerationRequest(BaseModel):
    description: str = Field(..., description="Description text to generate a GIF from")
    num_frames: Optional[int] = Field(6, description="Number of frames in the GIF")
    image_size: Optional[str] = Field("512x512", description="Size of the GIF frames")
    style: Optional[str] = Field("product", description="Style of the GIF")

class TrendPredictionRequest(BaseModel):
    product_name: str = Field(..., description="Name of the product")
    category: str = Field(..., description="Product category")
    target_demographic: str = Field(..., description="Target demographic")
    initial_price: float = Field(..., description="Initial price in USD")
    marketing_budget: float = Field(..., description="Marketing budget in USD")
    time_period: int = Field(30, description="Time period in days")
    seasonality_factor: float = Field(1.0, description="Seasonality factor (1.0-3.0)")
    competition_level: float = Field(0.5, description="Competition level (0.1-1.0)")

# Helper function for text generation
def generate_product_description(product_name, keywords="", tone="Professional", model_type="default"):
    """Generate product description using Gemini API"""
    try:
        logger.info(f"Generating description for product: {product_name}")
        
        # Check if the Gemini model is defined
        if 'gemini_model' not in globals():
            logger.error("Gemini model is not initialized")
            return {
                "success": False,
                "description": "Unable to generate description. Gemini API is not configured properly.",
                "status": "Error: Gemini model is not initialized"
            }
        
        tone_map = {
            "Professional": "formal, business-like, authoritative",
            "Casual": "relaxed, conversational, friendly",
            "Enthusiastic": "excited, energetic, passionate",
            "Formal": "polished, sophisticated, refined",
            "Friendly": "warm, approachable, personable"
        }
        
        tone_instructions = tone_map.get(tone, "professional and informative")
        
        prompt = f"""
        Generate a compelling product description for the following product:
        
        Product: {product_name}
        {"Keywords: " + keywords if keywords else ""}
        
        The description should:
        - Be written in a {tone_instructions} tone
        - Include 2-3 paragraphs
        - Highlight key features and benefits
        - Be creative and engaging
        - Use persuasive language
        - Appeal to the target audience
        - Include relevant emojis where appropriate
        
        Response should ONLY include the product description text.
        """
        
        logger.info("Sending request to Gemini API")
        response = gemini_model.generate_content(prompt)
        
        if not response:
            raise Exception("No response from Gemini API")
            
        description = response.text.strip()
        logger.info(f"Successfully generated description for {product_name}")
        
        return {
            "success": True,
            "description": description,
            "status": "Generated product description successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating description: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "description": "",
            "status": f"Error generating description: {str(e)}"
        }

# API routes
@app.get("/")
async def root():
    """Root endpoint to check API status"""
    return {
        "status": "online",
        "message": "Product AI Hub API is running",
        "endpoints": {
            "POST /generate-product-description": "Generate a product description",
            "POST /generate-product-image": "Generate a product image",
            "POST /generate-gif": "Generate an animated GIF from a description",
            "POST /generate-audio": "Generate audio from text",
            "GET /available-voices": "Get list of available voices",
            "POST /predict-trend": "Predict product trend",
            "POST /upload-image": "Upload an image for description generation",
            "POST /generate-description-from-image": "Generate a description from an uploaded image"
        }
    }

@app.post("/generate-product-description")
async def api_generate_product_description(request: TextGenerationRequest):
    """Generate a product description"""
    result = generate_product_description(
        request.product_name,
        request.keywords,
        request.tone,
        request.model_type
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["status"])
    return result

@app.post("/generate-product-image")
async def api_generate_product_image(request: ImageGenerationRequest):
    """Generate a product image"""
    status, image_path = generate_product_image(
        request.product_name,
        request.keywords,
        request.image_style,
        request.image_size
    )
    
    if not image_path:
        raise HTTPException(status_code=500, detail=status)
        
    # Get relative path for URL
    relative_path = image_path.replace('\\', '/')
    if '/' in relative_path:
        relative_path = '/' + '/'.join(relative_path.split('/')[1:])
    
    # Also create a static URL path for backward compatibility
    static_path = '/static' + relative_path
        
    return {
        "success": True,
        "image_url": relative_path,
        "static_image_url": static_path,
        "status": status
    }

@app.post("/generate-audio")
async def api_generate_audio(request: AudioGenerationRequest):
    """Generate audio from text"""
    logger.info(f"Generating audio for text: '{request.text[:50]}...' with voice: '{request.voice_id}'")
    
    status, audio_path = generate_audio(
        request.text,
        request.voice_id,
        request.style
    )
    
    if not audio_path:
        raise HTTPException(status_code=500, detail=status)
    
    logger.info(f"Audio generation successful, file saved at: {audio_path}")
        
    # Get just the filename without the directory
    filename = os.path.basename(audio_path)
      # Create multiple URL paths for the client to try
    direct_url = f"/get-audio/{filename}"  # Direct endpoint
    download_url = f"/direct-download/audio/{filename}"  # Direct download
    audio_url = f"/generated_audio/{filename}"  # Direct directory access
    static_audio_url = f"/static/generated_audio/{filename}"  # Via static directory
    
    logger.info(f"Audio URLs: direct={direct_url}, download={download_url}, audio_url={audio_url}, static={static_audio_url}")
        
    return {
        "success": True,
        "filename": filename,
        "audio_url": audio_url,
        "static_audio_url": static_audio_url,
        "direct_audio_url": direct_url,
        "download_url": download_url,
        "status": status
    }

@app.post("/generate-gif")
async def api_generate_gif(request: GifGenerationRequest):
    """Generate an animated GIF from a description"""
    status, gif_path = generate_gif_from_description(
        request.description,
        request.num_frames,
        request.image_size,
        request.style
    )
    
    if not gif_path:
        raise HTTPException(status_code=500, detail=status)
        
    # Get relative path for URL
    relative_path = gif_path.replace('\\', '/')
    if '/' in relative_path:
        relative_path = '/' + '/'.join(relative_path.split('/')[1:])
    
    # Also create a static URL path for backward compatibility
    static_path = '/static' + relative_path
    
    # Add a direct access URL as fallback
    filename = os.path.basename(gif_path)
    direct_url = f"/get-gif/{filename}"
        
    return {
        "success": True,
        "gif_url": relative_path,
        "static_gif_url": static_path,
        "direct_gif_url": direct_url,
        "status": status
    }

@app.get("/available-voices")
async def api_available_voices():
    """Get list of available voices"""
    return {
        "success": True,
        "voices": voice_descriptions
    }

@app.post("/generate-description-from-image")
async def generate_description_from_image(image: UploadFile = File(...)):
    """Generate a product description from an uploaded image"""
    # Create a temporary file to store the uploaded image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir="temp_uploads") as temp_file:
        shutil.copyfileobj(image.file, temp_file)
        temp_path = temp_file.name
    
    try:
        # Open the image with PIL
        from PIL import Image
        img = Image.open(temp_path)
        
        # Generate description from image
        description = image_desc_generator(img)
        
        # Remove the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if description.startswith("Error:"):
            raise HTTPException(status_code=500, detail=description)
            
        return {
            "success": True,
            "description": description,
            "status": "Generated description from uploaded image"
        }
    except Exception as e:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        logger.error(f"Error processing image: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/predict-trend")
async def api_predict_trend(request: TrendPredictionRequest):
    """Predict product trend"""
    # This is a placeholder - you should implement the actual trend prediction logic
    # using your existing product_trend_prediction.py module
    
    # Simulating a trend prediction response
    time_period = request.time_period
    start_date = datetime.now()
    dates = [(start_date.replace(day=start_date.day + i)).strftime("%Y-%m-%d") for i in range(time_period)]
    
    # Generate some example trend data
    base_factor = 1 + (request.initial_price / 1000) + (request.marketing_budget / 10000)
    competition_impact = 1 - request.competition_level * 0.5
    seasonality_impact = request.seasonality_factor
    
    base_trend = []
    for i in range(time_period):
        day_factor = 1 + (i / time_period) * 2  # Growth over time
        seasonal_factor = 1 + 0.2 * seasonality_impact * np.sin(i * np.pi / 15)  # Seasonal variation
        value = base_factor * day_factor * competition_impact * seasonal_factor * (0.9 + 0.2 * np.random.random())
        base_trend.append(round(value, 2))
    
    # Optimistic and pessimistic scenarios
    optimistic = [round(v * 1.3, 2) for v in base_trend]
    pessimistic = [round(v * 0.7, 2) for v in base_trend]
    
    return {
        "success": True,
        "data": {
            "product_name": request.product_name,
            "category": request.category,
            "target_demographic": request.target_demographic,
            "dates": dates,
            "base_trend": base_trend,
            "optimistic": optimistic,
            "pessimistic": pessimistic,
            "metrics": {
                "average_growth": f"{round((base_trend[-1] / base_trend[0] - 1) * 100, 1)}%",
                "peak_day": dates[base_trend.index(max(base_trend))],
                "peak_value": max(base_trend)
            },
            "recommendations": [
                f"Focus marketing efforts around {dates[time_period // 3]} to maximize initial growth",
                f"Consider promotional offers during peak day: {dates[base_trend.index(max(base_trend))]}",
                f"Plan for a potential {round((optimistic[-1] / base_trend[-1] - 1) * 100, 1)}% upside with optimal conditions"
            ]
        }
    }

@app.post("/upload-image")
async def api_upload_image(image: UploadFile = File(...)):
    """Upload an image for description generation"""
    # Create a temporary file to store the uploaded image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir="temp_uploads") as temp_file:
        shutil.copyfileobj(image.file, temp_file)
        temp_path = temp_file.name
    
    try:
        # Open the image with PIL
        from PIL import Image
        img = Image.open(temp_path)
        
        # Generate description from image
        description = image_desc_generator(img)
        
        # Remove the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if description.startswith("Error:"):
            raise HTTPException(status_code=500, detail=description)
            
        return {
            "success": True,
            "description": description,
            "status": "Generated description from uploaded image"
        }
    except Exception as e:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        logger.error(f"Error processing image: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
        
@app.post("/generate-description-from-image")
async def generate_description_from_image(image: UploadFile = File(...)):
    """Generate a product description from an uploaded image"""
    # Create a temporary file to store the uploaded image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir="temp_uploads") as temp_file:
        shutil.copyfileobj(image.file, temp_file)
        temp_path = temp_file.name
    
    try:
        # Open the image with PIL
        from PIL import Image
        img = Image.open(temp_path)
        
        # Generate description from image
        description = image_desc_generator(img)
        
        # Remove the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if description.startswith("Error:"):
            raise HTTPException(status_code=500, detail=description)
            
        return {
            "success": True,
            "description": description,
            "status": "Generated description from uploaded image"
        }
    except Exception as e:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        logger.error(f"Error processing image: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/get-gif/{gif_filename}")
async def get_gif(gif_filename: str):
    """Get a GIF file by its filename"""
    # Try multiple possible paths
    possible_paths = [
        os.path.join("generated_gifs", gif_filename),
        os.path.join("static", "generated_gifs", gif_filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return FileResponse(path, media_type="image/gif")
    
    # If file not found
    raise HTTPException(status_code=404, detail=f"GIF file '{gif_filename}' not found")

@app.get("/get-audio/{audio_filename}")
async def get_audio(audio_filename: str):
    """Get an audio file by its filename"""
    logger.info(f"Request to access audio file: {audio_filename}")
    
    # Try multiple possible paths
    possible_paths = [
        os.path.join("generated_audio", audio_filename),
        os.path.join("static", "generated_audio", audio_filename)
    ]
    
    logger.info(f"Checking paths: {possible_paths}")
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found audio file at: {path}")
            return FileResponse(path, media_type="audio/mpeg")
        else:
            logger.warning(f"Audio file not found at: {path}")
    
    # If we get here, the file wasn't found - check what files exist
    try:
        if os.path.exists("generated_audio") and os.path.isdir("generated_audio"):
            existing_files = os.listdir("generated_audio")
            logger.warning(f"Files in generated_audio: {existing_files}")
        if os.path.exists("static/generated_audio") and os.path.isdir("static/generated_audio"):
            existing_files = os.listdir("static/generated_audio")
            logger.warning(f"Files in static/generated_audio: {existing_files}")
    except Exception as e:
        logger.error(f"Error checking directories: {e}")
    
    # If file not found
    raise HTTPException(status_code=404, detail=f"Audio file '{audio_filename}' not found")

@app.get("/direct-download/audio/{audio_filename}")
async def direct_download_audio(audio_filename: str):
    """Direct download endpoint for audio files that bypasses static file serving"""
    logger.info(f"Direct download request for audio file: {audio_filename}")
    
    # Check both main locations
    possible_paths = [
        os.path.join("generated_audio", audio_filename),
        os.path.join("static", "generated_audio", audio_filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isfile(path):
            # Get absolute path
            abs_path = os.path.abspath(path)
            logger.info(f"Found file at {abs_path}, returning for direct download")
            
            # Return file with attachment disposition to force download
            return FileResponse(
                path=abs_path, 
                media_type="audio/mpeg",
                filename=audio_filename
            )
    
    # If we get here, log all audio files for debugging
    audio_files = []
    if os.path.exists("generated_audio"):
        audio_files.extend([f"generated_audio/{f}" for f in os.listdir("generated_audio") if f.endswith(".mp3")])
    if os.path.exists("static/generated_audio"):
        audio_files.extend([f"static/generated_audio/{f}" for f in os.listdir("static/generated_audio") if f.endswith(".mp3")])
    
    logger.error(f"File {audio_filename} not found. Available audio files: {audio_files}")
    
    raise HTTPException(status_code=404, detail=f"Audio file '{audio_filename}' not found")

@app.get("/debug-static-paths")
async def debug_static_paths():
    """Debug endpoint to check static file paths"""
    # Check directories
    dirs = {
        "generated_gifs": os.path.exists("generated_gifs") and os.path.isdir("generated_gifs"),
        "generated_audio": os.path.exists("generated_audio") and os.path.isdir("generated_audio"),
        "generated_images": os.path.exists("generated_images") and os.path.isdir("generated_images"),
        "static": os.path.exists("static") and os.path.isdir("static"),
        "static/generated_gifs": os.path.exists("static/generated_gifs") and os.path.isdir("static/generated_gifs"),
        "static/generated_audio": os.path.exists("static/generated_audio") and os.path.isdir("static/generated_audio"),
        "static/generated_images": os.path.exists("static/generated_images") and os.path.isdir("static/generated_images")
    }
    
    # List files
    files = {
        "generated_gifs": os.listdir("generated_gifs") if dirs["generated_gifs"] else [],
        "generated_audio": os.listdir("generated_audio") if dirs["generated_audio"] else [],
        "static/generated_gifs": os.listdir("static/generated_gifs") if dirs["static/generated_gifs"] else [],
        "static/generated_audio": os.listdir("static/generated_audio") if dirs["static/generated_audio"] else []
    }
    
    # Check if the static directories are symlinks
    symlinks = {
        "static/generated_gifs": os.path.islink("static/generated_gifs") if os.path.exists("static/generated_gifs") else False,
        "static/generated_audio": os.path.islink("static/generated_audio") if os.path.exists("static/generated_audio") else False,
        "static/generated_images": os.path.islink("static/generated_images") if os.path.exists("static/generated_images") else False
    }
    
    # Return all debug info
    return {
        "directories": dirs,
        "files": files,
        "symlinks": symlinks,
        "os_type": os.name,
        "app_mounted_paths": [
            "/static",
            "/generated_images",
            "/generated_audio",
            "/generated_gifs"
        ]
    }

@app.get("/test-audio-access/{audio_filename}")
async def test_audio_access(audio_filename: str):
    """Test endpoint to verify audio file exists and can be accessed"""
    logger.info(f"Testing access to audio file: {audio_filename}")
    
    # Check all possible paths
    paths_to_check = [
        os.path.join("generated_audio", audio_filename),
        os.path.join("static", "generated_audio", audio_filename),
        os.path.join(os.getcwd(), "generated_audio", audio_filename),
        os.path.join(os.getcwd(), "static", "generated_audio", audio_filename)
    ]
    
    results = {}
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                size = os.path.getsize(path)
                results[path] = {
                    "exists": True,
                    "size_bytes": size,
                    "is_file": os.path.isfile(path),
                    "is_readable": os.access(path, os.R_OK)
                }
            except Exception as e:
                results[path] = {
                    "exists": True,
                    "error": str(e)
                }
        else:
            results[path] = {
                "exists": False
            }
    
    # Check what URLs would be served
    urls = {
        "/generated_audio/{filename}": f"/generated_audio/{audio_filename}",
        "/static/generated_audio/{filename}": f"/static/generated_audio/{audio_filename}",
        "/get-audio/{filename}": f"/get-audio/{audio_filename}",
        "/direct-download/audio/{filename}": f"/direct-download/audio/{audio_filename}"
    }
    
    # List all audio files in both directories
    all_audio_files = []
    if os.path.exists("generated_audio") and os.path.isdir("generated_audio"):
        all_audio_files.extend([f"generated_audio/{f}" for f in os.listdir("generated_audio") if f.endswith(".mp3")])
    if os.path.exists("static/generated_audio") and os.path.isdir("static/generated_audio"):
        all_audio_files.extend([f"static/generated_audio/{f}" for f in os.listdir("static/generated_audio") if f.endswith(".mp3")])
    
    return {
        "filename": audio_filename,
        "path_checks": results,
        "urls": urls,
        "all_audio_files": all_audio_files,
        "current_directory": os.getcwd(),
        "static_mount_point": "/static → static directory",
        "generated_audio_mount_point": "/generated_audio → generated_audio directory"
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)
