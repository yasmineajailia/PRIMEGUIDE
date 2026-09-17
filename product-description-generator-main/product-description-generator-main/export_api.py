from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import traceback
import uvicorn
from io import BytesIO
from PIL import Image

# Import the model generators
from generators.text_generator import product_desc_generator, generate_with_t5, generate_with_flan_t5
from generators.image_generator import generate_product_image, image_desc_generator
from generators.gif_generator import generate_gif_from_description
from website_generator import WebsiteGenerator

# Create FastAPI app
app = FastAPI(title="Product Generator API")

# Create website generator instance
website_generator = WebsiteGenerator()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("generated_images", exist_ok=True)
os.makedirs("generated_gifs", exist_ok=True)
os.makedirs("generated_websites", exist_ok=True)

# Model request classes
class ProductDescriptionRequest(BaseModel):
    product_name: str
    keywords: str = ""
    tone: str = "Professional"
    model_type: str = "default"  # options: default, t5, flan-t5

class ProductImageRequest(BaseModel):
    product_name: str
    keywords: str = ""
    image_style: str = "product"  # options: product, realistic, artistic, minimalist, isometric
    image_size: str = "512x512"

class ProductGifRequest(BaseModel):
    description_text: str
    num_frames: int = 6
    image_size: str = "512x512"
    style: str = "product"  # options: product, realistic, artistic, minimalist, isometric

# New request model for website generation
class WebsiteGenerationRequest(BaseModel):
    product_name: str
    product_description: str
    image_path: str = None 
    gif_path: str = None
    features: list[str] = None

class CombinedGenerationRequest(BaseModel):
    product_name: str
    keywords: str = ""
    tone: str = "Professional"
    image_style: str = "product"
    num_gif_frames: int = 6
    image_size: str = "512x512"

# API endpoints
@app.get("/")
async def root():
    return {"message": "Product Generator API is running"}

@app.post("/generate-product-description")
async def generate_product_description(request: ProductDescriptionRequest):
    try:
        print(f"Received product description request: {request}")
        
        # Generate description based on the requested model type
        if request.model_type == "t5":
            description = generate_with_t5(request.product_name)
        elif request.model_type == "flan-t5":
            description = generate_with_flan_t5(request.product_name)
        else:
            # Default to the product_desc_generator
            description = product_desc_generator(request.product_name, request.keywords, request.tone)
            
        return {"success": True, "description": description}
    except Exception as e:
        print(f"Error in generate_product_description: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

@app.post("/generate-product-image")
async def generate_image(request: ProductImageRequest):
    try:
        print(f"Received product image generation request: {request}")
        
        # Generate the product image
        status, image_path = generate_product_image(
            request.product_name, 
            request.keywords, 
            request.image_style, 
            request.image_size
        )
        
        # Return image URL for client to access
        if image_path:
            # Convert local path to URL path
            image_url = f"/static/{os.path.basename(image_path)}"
            return {"success": True, "status": status, "image_url": image_url, "local_path": image_path}
        else:
            return {"success": False, "status": status, "image_url": None}
    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

@app.post("/generate-product-gif")
async def generate_gif(request: ProductGifRequest):
    try:
        print(f"Received product GIF generation request: {request}")
        
        # Generate the product GIF
        status, gif_path = generate_gif_from_description(
            request.description_text, 
            request.num_frames, 
            request.image_size, 
            request.style
        )
        
        # Return GIF URL for client to access
        if gif_path:
            # Convert local path to URL path
            gif_url = f"/static-gifs/{os.path.basename(gif_path)}"
            return {"success": True, "status": status, "gif_url": gif_url, "local_path": gif_path}
        else:
            return {"success": False, "status": status, "gif_url": None}
    except Exception as e:
        print(f"Error in generate_gif: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

@app.post("/generate-description-from-image")
async def generate_description_from_image(image: UploadFile = File(...)):
    """Generate a product description from an uploaded image"""
    try:
        print(f"Received image description generation request")
        
        # Read the image file
        contents = await image.read()
        pil_image = Image.open(BytesIO(contents))
        
        # Generate description from image
        description = image_desc_generator(pil_image)
        
        return {"success": True, "description": description}
    except Exception as e:
        print(f"Error in generate_description_from_image: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

@app.post("/generate-website")
async def generate_website(request: WebsiteGenerationRequest):
    """Generate a product website from a description, image, and/or GIF"""
    try:
        print(f"Received website generation request: {request}")
        
        # Generate the website
        website_path = website_generator.generate_website(request.dict())
        
        # Get the URL path (relative to /static-sites)
        relative_path = os.path.basename(website_path)
        website_url = f"/static-sites/{relative_path}"
        
        return {
            "success": True, 
            "website_url": website_url,
            "local_path": website_path
        }
    except Exception as e:
        print(f"Error in generate_website: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

@app.post("/generate-everything")
async def generate_everything(request: CombinedGenerationRequest):
    """Generate product description, image, GIF, and website in one request"""
    try:
        print(f"Received combined generation request: {request}")
        results = {}
        
        # 1. Generate product description
        desc_result = await generate_product_description(
            ProductDescriptionRequest(
                product_name=request.product_name,
                keywords=request.keywords,
                tone=request.tone
            )
        )
        results["description"] = desc_result["description"]
        
        # 2. Generate product image
        image_result = await generate_image(
            ProductImageRequest(
                product_name=request.product_name,
                keywords=request.keywords,
                image_style=request.image_style,
                image_size=request.image_size
            )
        )
        results["image_path"] = image_result.get("local_path")
        
        # 3. Generate product GIF
        gif_result = await generate_gif(
            ProductGifRequest(
                description_text=results["description"],
                num_frames=request.num_gif_frames,
                image_size=request.image_size,
                style=request.image_style
            )
        )
        results["gif_path"] = gif_result.get("local_path")
        
        # 4. Extract features from description (simple heuristic)
        features = [
            line.strip()[2:] for line in results["description"].split("\n") 
            if line.strip().startswith("- ")
        ]
        
        # 5. Generate product website
        website_result = await generate_website(
            WebsiteGenerationRequest(
                product_name=request.product_name,
                product_description=results["description"],
                image_path=results["image_path"],
                gif_path=results["gif_path"],
                features=features
            )
        )
        
        return {
            "success": True,
            "description": results["description"],
            "image_url": image_result.get("image_url"),
            "gif_url": gif_result.get("gif_url"),
            "website_url": website_result["website_url"],
            "features": features
        }
    except Exception as e:
        print(f"Error in generate_everything: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

# Serve static files for generated content
try:
    app.mount("/static", StaticFiles(directory="generated_images"), name="static_images")
    app.mount("/static-gifs", StaticFiles(directory="generated_gifs"), name="static_gifs")
    app.mount("/static-sites", StaticFiles(directory="generated_websites"), name="static_sites")
except Exception as e:
    print(f"Warning: Could not configure static file serving: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
