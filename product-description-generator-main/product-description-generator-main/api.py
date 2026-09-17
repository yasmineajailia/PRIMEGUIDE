from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import os
import traceback
import json
import pandas as pd
from dotenv import load_dotenv
import torch
import numpy as np

class SimpleTrendPredictor:
    def __init__(self, data_path='data/product_trends.csv'):
        self.data_path = data_path
        self.trend_data = self._load_data()
    
    def _load_data(self):
        try:
            df = pd.read_csv(self.data_path)
            print(f"Loaded trend data with {len(df)} rows")
            return df
        except Exception as e:
            print(f"Error loading trend data: {e}")
            return pd.DataFrame()
    
    def predict(self, product_name: str, category: str, initial_price: float, 
               marketing_budget: float, time_period: int, 
               seasonality_factor: float, competition_level: float) -> dict:
        try:
            # Generate some sample predictions based on inputs
            base_sales = initial_price * 0.1  # Base sales as percentage of price
            
            # Generate trend based on marketing budget and competition
            trend_factor = (marketing_budget / 1000) * (1 - competition_level)
            
            # Generate time series data
            time_points = list(range(1, time_period + 1))
            predicted_sales = [
                base_sales * (1 + trend_factor * t + 
                             seasonality_factor * np.sin(2 * np.pi * t / 12))  # Monthly seasonality
                for t in time_points
            ]
            
            # Calculate metrics
            peak_sales = max(predicted_sales)
            avg_sales = sum(predicted_sales) / len(predicted_sales)
            roi = (sum(predicted_sales) * initial_price - marketing_budget) / marketing_budget * 100
            
            return {
                "product_name": product_name,
                "category": category,
                "predicted_sales": [round(x, 2) for x in predicted_sales],
                "time_periods": time_points,
                "peak_sales": round(peak_sales, 2),
                "average_sales": round(avg_sales, 2),
                "roi": round(roi, 2),
                "recommendations": [
                    f"Consider increasing marketing budget by {int(seasonality_factor * 20)}% during peak seasons"
                    if seasonality_factor > 1 else "Maintain consistent marketing efforts",
                    "Focus on competitive pricing strategy" if competition_level > 0.5 
                    else "Focus on product differentiation"
                ]
            }
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            print(traceback.format_exc())
            raise

class SimpleMarketingRecommender:
    def __init__(self, data_path='data/marketing_strategies.csv'):
        self.data_path = data_path
        self.strategies = self._load_data()
    
    def _load_data(self):
        try:
            df = pd.read_csv(self.data_path)
            print(f"Loaded {len(df)} marketing strategies")
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading marketing strategies: {e}")
            return []
    
    def recommend(self, industry: str, budget_amount: float, daily_hours: float,
                 technical_skill: int, audience_size: str, goal: str) -> list:
        try:
            if not self.strategies:
                return self._get_default_recommendations()
                
            # Filter strategies based on inputs
            filtered = []
            for strat in self.strategies:
                # Simple filtering logic - can be enhanced
                if (strat.get('budget_required', float('inf')) <= budget_amount and
                    strat.get('time_investment', 0) <= daily_hours and
                    strat.get('technical_skill_required', 5) <= technical_skill):
                    filtered.append(strat)
            
            # If no strategies match, return default
            if not filtered:
                return self._get_default_recommendations()
                
            # Sort by ROI or other metric
            return sorted(filtered, key=lambda x: x.get('expected_roi', 0), reverse=True)[:5]
            
        except Exception as e:
            print(f"Error in recommendation: {str(e)}")
            return self._get_default_recommendations()
    
    def _get_default_recommendations(self):
        return [
            {
                "strategy_name": "Social Media Marketing",
                "description": "Increase presence on social media platforms",
                "expected_roi": 200,
                "budget_required": 1000,
                "time_investment": 10
            },
            {
                "strategy_name": "Email Campaigns",
                "description": "Run targeted email marketing campaigns",
                "expected_roi": 180,
                "budget_required": 800,
                "time_investment": 8
            }
        ]

# Initialize the models
try:
    trend_predictor = SimpleTrendPredictor()
    marketing_recommender = SimpleMarketingRecommender()
    print("Models initialized successfully")
except Exception as e:
    print(f"Error initializing models: {e}")
    traceback.print_exc()

# Load environment variables
load_dotenv()

app = FastAPI(title="Product Description Generator API")

# CORS middleware to allow requests from your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],  # Default React development port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import model generators
from generators.text_generator import product_desc_generator, generate_with_t5, generate_with_flan_t5
from generators.image_generator import generate_product_image
from generators.gif_generator import generate_gif_from_description

# Initialize the models lazily to improve startup time
text_generator_initialized = False
image_generator_initialized = False
gif_generator_initialized = False

# Request models
class ProductTrendRequest(BaseModel):
    product_name: str
    category: str
    initial_price: float
    marketing_budget: float
    time_period: int
    seasonality_factor: float
    competition_level: float

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

class MarketingRecommendationRequest(BaseModel):
    industry: str
    budget_amount: float
    daily_hours: float
    technical_skill: int
    audience_size: str
    goal: str

# Error handler for 500 errors
@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "traceback": traceback.format_exc()
        }
    )

# Endpoints
@app.get("/")
async def root():
    return {"message": "Product Description Generator API is running"}

@app.post("/predict-trend")
async def predict_trend(request: ProductTrendRequest):
    try:
        print(f"Received request: {request}")
        
        # Use the predictor
        trend_data = trend_predictor.predict(
            request.product_name,
            request.category,
            request.initial_price,
            request.marketing_budget,
            request.time_period,
            request.seasonality_factor,
            request.competition_level
        )
        return {"success": True, "data": trend_data}
    except Exception as e:
        print(f"Error in predict_trend: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

@app.post("/get-marketing-recommendations")
async def get_recommendations(request: MarketingRecommendationRequest):
    try:
        print(f"Received recommendation request: {request}")
        # Use the recommender
        recommendations = marketing_recommender.recommend(
            request.industry,
            request.budget_amount,
            request.daily_hours,
            request.technical_skill,
            request.audience_size,
            request.goal
        )
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

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
        
        # Return image URL for client to access (assumes serving static files)
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
        
        # Return GIF URL for client to access (assumes serving static files)
        if gif_path:
            # Convert local path to URL path
            gif_url = f"/static/{os.path.basename(gif_path)}"
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

# Serve static files for images and GIFs
from fastapi.staticfiles import StaticFiles
try:
    # Mount directories for generated content
    app.mount("/static", StaticFiles(directory="generated_images"), name="static_images")
    app.mount("/static/gifs", StaticFiles(directory="generated_gifs"), name="static_gifs")
    print("Static file serving configured")
except Exception as e:
    print(f"Warning: Could not configure static file serving: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
