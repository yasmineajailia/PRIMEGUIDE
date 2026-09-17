from __future__ import annotations
import torch
torch.set_default_device('cpu')
import os
import gradio as gr
import types
from diffusers.pipelines.animatediff import pipeline_animatediff
import numpy as np
import pandas as pd
import textstat
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
from sentence_transformers import SentenceTransformer
import tempfile
import webbrowser
from simple_recommender import SimpleMarketingRecommender
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from test_trend_prediction import TrendPredictor

# Make FAISS import optional due to installation issues
try:
    import faiss
    faiss_available = True
except ImportError:
    faiss_available = False
    print("Warning: FAISS not available, using alternative similarity search")
    from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
try:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        print("Google Generative AI configured successfully")
    else:
        print("No Google API key found. Ad campaign generation will be disabled.")
        gemini_model = None
except Exception as e:
    print(f"Error configuring Google Generative AI: {e}")
    gemini_model = None

# Configure ElevenLabs for audio generation
try:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        eleven_client = ElevenLabs(api_key=api_key)
        print("ElevenLabs API configured successfully")
    else:
        print("No ElevenLabs API key found. Audio generation will be disabled.")
        eleven_client = None
except Exception as e:
    print(f"Error configuring ElevenLabs: {e}")
    eleven_client = None

# Import components
from utils.dataset import visualize_dataset
from generators.text_generator import product_desc_generator, generate_with_t5, generate_with_flan_t5
from generators.image_generator import image_desc_generator, generate_product_image
from generators.gif_generator import generate_gif_from_description
from trainers.t5_trainer import finetune_t5_on_dataset
from trainers.flan_t5_trainer import finetune_flan_t5_on_dataset

# Store the original encode_prompt method
original_encode_prompt = pipeline_animatediff.AnimateDiffPipeline.encode_prompt
# Define a patched version that forces CPU usage
def patched_encode_prompt(self, prompt, device="cpu", num_images_per_prompt=1, do_classifier_free_guidance=True, negative_prompt=None, prompt_embeds=None, negative_prompt_embeds=None, lora_scale=None, clip_skip=None):
    # Call the original method but force device to be "cpu"
    return original_encode_prompt(self, prompt, device="cpu", num_images_per_prompt=num_images_per_prompt, 
                                 do_classifier_free_guidance=do_classifier_free_guidance, 
                                 negative_prompt=negative_prompt, prompt_embeds=prompt_embeds,
                                 negative_prompt_embeds=negative_prompt_embeds, 
                                 lora_scale=lora_scale, clip_skip=clip_skip)

# Replace the original method with our patched version
pipeline_animatediff.AnimateDiffPipeline.encode_prompt = patched_encode_prompt

# --- Configuration ---
# Path to the dataset used for fine-tuning the underlying model concept
dataset_path = os.path.join("data", "t5_product_description_data.csv")
# Path where the fine-tuned model *would* be saved (simulation)
finetuned_model_path = "data/simulated_finetuned_model"
# Directory to store generated GIFs temporarily
output_gif_dir = "generated_gifs"
# Ensure the output directory exists
os.makedirs(output_gif_dir, exist_ok=True)
os.makedirs("models", exist_ok=True)

# Voice descriptions
voice_descriptions = {
    "Aria": "Bright and expressive female voice",
    "Roger": "Deep and composed male voice",
    "Sarah": "Soft and reassuring female voice",
    "Laura": "Warm and enthusiastic female voice",
    "Charlie": "Young and natural male voice",
}

# ========== Data and Index Functions ==========

def load_advertising_data():
    """Load advertising campaign data for RAG"""
    entries = []
    try:
        if os.path.exists("entries.csv"):
            return pd.read_csv("entries.csv").to_dict(orient="records")
            
        # Try to load Social Media Advertising data
        if os.path.exists("data/Social_Media_Advertising.csv"):
            df_social = pd.read_csv("data/Social_Media_Advertising.csv")
            for _, row in df_social.iterrows():
                entries.append(
                    {
                        "product": str(row.get("Campaign_Goal", "")).lower(),
                        "target": str(row.get("Target_Audience", "")).lower(),
                        "format": str(row.get("Channel_Used", "")).lower(),
                        "completion": f"Campaign '{row.get('Campaign_Goal', '')}' on {row.get('Channel_Used', '')} for {row.get('Target_Audience', '')} | ROI: {row.get('ROI', '')}, engagement: {row.get('Engagement_Score', '')}",
                    }
                )
                
        # Try to load Amazon data
        if os.path.exists("data/train.csv"):
            df_amazon = pd.read_csv(
                "data/train.csv", sep=",", quoting=3, on_bad_lines="skip", low_memory=False
            )
            for _, row in df_amazon.iterrows():
                bullet_points = str(row.get("BULLET_POINTS", "")).replace("\n", " ")
                description = str(row.get("DESCRIPTION", "")).replace("\n", " ")
                entries.append(
                    {
                        "product": str(row.get("TITLE", "")).lower(),
                        "target": "general",
                        "format": "amazon",
                        "completion": f"{bullet_points} {description}",
                    }
                )
                
        # Try to load Digital Marketing Campaigns data
        if os.path.exists("data/digital_marketing_campaigns_smes.csv"):
            df = pd.read_csv("data/digital_marketing_campaigns_smes.csv")
            for _, row in df.iterrows():
                entries.append(
                    {
                        "product": str(row.get("industry", "")).lower(),
                        "target": str(row.get("target_audience", "")).lower(),
                        "format": str(row.get("marketing_channel", "")).lower(),
                        "completion": f"Conversion: {row.get('conversion_rate', '')}, engagement: {row.get('engagement_rate', '')}",
                    }
                )
        
        # Save the entries for future use
        if entries:
            pd.DataFrame(entries).to_csv("entries.csv", index=False)
            
    except Exception as e:
        print(f"Error loading advertising data: {e}")
        
    return entries

def load_or_build_embeddings(entries):
    """Load or build embeddings for semantic search"""
    try:
        if os.path.exists("embeddings.npy"):
            embeddings = np.load("embeddings.npy")
            return embeddings
            
        # Load embedding model if not already loaded
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Build embeddings
        print("Building embeddings...")
        texts = [f"{e.get('product', '')} {e.get('target', '')} {e.get('format', '')}" for e in entries]
        embeddings = embed_model.encode(texts, convert_to_numpy=True)
        
        # Save for future use
        np.save("embeddings.npy", embeddings)
        return embeddings
        
    except Exception as e:
        print(f"Error with embeddings: {e}")
        return None

def semantic_search(query, entries, embeddings, top_k=3):
    """Find semantically similar advertising examples"""
    if not entries or embeddings is None:
        return []
    
    try:
        # Load embedding model
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Encode query
        query_vector = embed_model.encode([query])[0].reshape(1, -1)
        
        # Do search based on available libraries
        if faiss_available:
            # Create FAISS index in memory
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            
            # Search
            distances, indices = index.search(np.array([query_vector[0]]), top_k)
            return [entries[idx] for idx in indices[0]]
        else:
            # Fallback to cosine similarity
            similarities = cosine_similarity(query_vector, embeddings)[0]
            top_indices = similarities.argsort()[-top_k:][::-1]
            return [entries[idx] for idx in top_indices]
            
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []

def generate_ad_campaign(product, target, ad_format):
    """Generate advertising campaign using RAG with Gemini"""
    if not gemini_model:
        return "Google Generative AI API key not configured. Please add it to your .env file."
    
    try:
        # Load data and embeddings
        entries = load_advertising_data()
        embeddings = load_or_build_embeddings(entries)
        
        # Find similar examples using search
        examples = semantic_search(f"{product} {target} {ad_format}", entries, embeddings)
        
        # Handle case where no examples are found
        if not examples:
            return f"No similar examples found. Please try different inputs."
            
        # Generate with Retrieval Augmented Generation
        example_texts = "\n".join([f"- {ex.get('completion', 'Example campaign')}" for ex in examples])
        prompt = (
            f"Here are examples of similar advertising campaigns:\n"
            f"{example_texts}\n\n"
            f"Now, generate a creative campaign adapted to the following context:\n"
            f"- Product: {product}\n"
            f"- Target audience: {target}\n"
            f"- Advertising format: {ad_format}\n"
            f"→ The message should be engaging, original, relevant for a small business, and professionally written."
        )
        
        response = gemini_model.generate_content(prompt)
        result = response.text
        
        # Add metrics
        readability = textstat.flesch_reading_ease(result)
        age_level = textstat.text_standard(result)
        
        # Format the result with metrics
        final_result = f"{result}\n\n---\n📊 Readability score: {readability}/100\n📚 Reading level: {age_level}"
        
        return final_result
        
    except Exception as e:
        return f"Error generating ad campaign: {str(e)}"

def generate_audio(text, voice_id):
    """Generate audio from text using ElevenLabs"""
    if not eleven_client:
        return None, "ElevenLabs API key not configured"
    
    if not text:
        return None, "No text provided for audio generation"
    
    try:
        audio = eleven_client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.4, similarity_boost=0.75, style=0.5
            ),
        )
        
        audio_bytes = b"".join(audio)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(audio_bytes)
            temp_audio_path = f.name
        
        return temp_audio_path, f"Audio generated using voice: {voice_id}"
        
    except Exception as e:
        return None, f"Error generating audio: {str(e)}"

def get_marketing_recommendations(industry, budget_amount, daily_hours, technical_skill, audience_size, goal):
    """Generate marketing strategy recommendations based on inputs"""
    try:
        # Initialize the recommender
        recommender = SimpleMarketingRecommender()
        
        # Format preferences
        prefs = {
            'budget_amount': int(float(budget_amount)),
            'daily_hours': int(float(daily_hours)),
            'technical_skill': int(float(technical_skill)),
            'goal': goal,
            'industry': industry,
            'audience_size': int(float(audience_size))
        }
        
        # Get recommendations
        recommendations = recommender.get_recommendations(prefs, top_n=3, include_trends=True)
        
        if not recommendations:
            return "No matching strategies found for your criteria."
        
        # Format the results
        result = "🎯 TOP MARKETING STRATEGIES\n" + "=" * 60 + "\n\n"
        
        for i, (strategy, similarity) in enumerate(recommendations, 1):
            result += f"#{i} {strategy['strategy_name']} (Match: {similarity:.2f})\n"
            result += f"- Best for: {strategy['best_for_industry']}\n"
            result += f"- Budget: {'$' * strategy['budget_required']} ({strategy['budget_required']}/5)\n"
            result += f"- Expertise: {'*' * strategy['technical_expertise']} ({strategy['technical_expertise']}/5)\n" 
            result += f"- Time: {'⏱' * strategy['time_investment']} ({strategy['time_investment']}/5)\n"
            result += f"- Conversion: {'↑' * strategy['conversion_rate']} ({strategy['conversion_rate']}/5)\n"
            result += f"- Awareness: {'👁' * strategy['brand_awareness']} ({strategy['brand_awareness']}/5)\n"
            result += f"- Leads: {'⚡' * strategy['lead_generation']} ({strategy['lead_generation']}/5)\n"
            result += f"- Retention: {'♥' * strategy['customer_retention']} ({strategy['customer_retention']}/5)\n"
            
            if 'trend_metrics' in strategy:
                result += f"- Trend Effectiveness: {strategy['trend_metrics']['effectiveness']:.2f}\n"
                result += f"- Cost Efficiency: {strategy['trend_metrics']['cost_efficiency']:.2f}\n"
                result += f"- Adoption Rate: {strategy['trend_metrics']['adoption_rate']:.2f}\n"
            
            result += "-" * 60 + "\n\n"
            
        return result
        
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

def get_all_industries():
    """Get a list of all industries from marketing strategies data"""
    try:
        recommender = SimpleMarketingRecommender()
        all_industries = set()
        for strategy in recommender.strategies:
            industries = strategy['best_for_industry'].replace('"', '').split(',')
            all_industries.update([i.strip() for i in industries])
        return sorted(list(all_industries))
    except Exception as e:
        print(f"Error getting industries: {e}")
        return ["retail", "technology", "healthcare", "education", "finance", "food"]

def predict_product_trend(product_name, category, initial_price, marketing_budget, 
                         time_period, seasonality_factor, competition_level):
    """Generate product trend predictions based on inputs"""
    try:
        # Convert inputs to appropriate types
        initial_price = float(initial_price)
        marketing_budget = float(marketing_budget)
        time_period = int(time_period)
        seasonality_factor = float(seasonality_factor)
        competition_level = float(competition_level)
        
        # Create a predictor instance (using your TrendPredictor or a simplified version)
        predictor = TrendPredictor()
        
        # Generate prediction data
        dates = [datetime.now() + timedelta(weeks=i) for i in range(time_period)]
        
        # Base trend with seasonality
        base_trend = []
        for i in range(time_period):
            # Start with a base value
            value = initial_price * 0.10  # 10% of price as base sales
            
            # Add growth over time (higher marketing budget = faster growth)
            growth = (marketing_budget / 1000) * (i / time_period) * 1.5
            
            # Add seasonality effect (varies based on seasonality factor)
            season = seasonality_factor * np.sin(i * 2 * np.pi / 52)  # 52 weeks in a year
            
            # Competition reduces growth over time
            competition_effect = 1.0 - (competition_level * i / (time_period * 10))
            
            # Calculate prediction with all factors
            prediction = (value + growth + season) * competition_effect
            base_trend.append(max(0, prediction))  # Ensure non-negative
        
        # Create optimistic and pessimistic scenarios
        optimistic = [val * 1.3 for val in base_trend]
        pessimistic = [val * 0.7 for val in base_trend]
        
        # Calculate ROI
        total_sales = sum(base_trend)
        total_revenue = total_sales * initial_price
        roi = ((total_revenue - marketing_budget) / marketing_budget) * 100 if marketing_budget > 0 else 0
        
        # Generate plot
        plt.figure(figsize=(10, 6))
        plt.plot([d.strftime('%m/%d') for d in dates], base_trend, 'b-', label='Expected')
        plt.plot([d.strftime('%m/%d') for d in dates], optimistic, 'g--', label='Optimistic')
        plt.plot([d.strftime('%m/%d') for d in dates], pessimistic, 'r--', label='Pessimistic')
        plt.xlabel('Date')
        plt.ylabel('Projected Sales')
        plt.title(f'Sales Forecast for {product_name}')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save plot to memory
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        # Convert BytesIO to PIL Image
        from PIL import Image
        img = Image.open(buf)
        
        # Create summary text
        summary = f"""## Product Trend Forecast: {product_name}

**Category:** {category}
**Time Period:** {time_period} weeks
**Initial Price:** ${initial_price:.2f}
**Marketing Budget:** ${marketing_budget:.2f}

### Forecast Results:
- **Peak Sales (Expected):** {max(base_trend):.1f} units/week
- **Projected Total Sales:** {sum(base_trend):.1f} units
- **Estimated Revenue:** ${sum(base_trend) * initial_price:.2f}
- **Projected ROI:** {roi:.1f}%

### Key Factors:
- Seasonality Impact: {"High" if seasonality_factor > 0.5 else "Medium" if seasonality_factor > 0.2 else "Low"}
- Competition Level: {"High" if competition_level > 0.7 else "Medium" if competition_level > 0.4 else "Low"}
"""
        
        # Return the chart as PIL Image and summary
        return img, summary
        
    except Exception as e:
        return None, f"Error generating product trend forecast: {str(e)}"

# --- Gradio Interface ---
with gr.Blocks() as demo:
    

    with gr.Tab("Generate from Text"):
        product_name_input = gr.Textbox(
            label="Product Name",
            placeholder="Example: Eco-Friendly Bamboo Toothbrush Set",
        )
        text_keywords_input = gr.Textbox(
            label="Keywords (separated by commas)",
            placeholder="Example: sustainable, biodegradable, soft bristles, pack of 4",
        )
        tone_choices = gr.Dropdown(
            label="Select Tone",
            choices=["Professional", "Casual", "Enthusiastic", "Luxury", "Technical", "Minimalist"], 
            value="Professional"
        )
        text_product_description_output = gr.Textbox(label="Generated Product Description")
        text_generate_button = gr.Button(value="Generate Description!")
        text_generate_button.click(
            product_desc_generator,
            inputs=[product_name_input, text_keywords_input, tone_choices],
            outputs=text_product_description_output
        )

    with gr.Tab("Generate from Image"):
        image_input = gr.Image(type="pil", label="Upload Product Image")
        image_product_description_output = gr.Textbox(label="Generated Product Description")
        image_generate_button = gr.Button(value="Generate Description from Image!")
        image_generate_button.click(
            image_desc_generator,
            inputs=[image_input],
            outputs=image_product_description_output
        )

    with gr.Tab("Generate GIF from Description"):
        gif_description_input = gr.Textbox(
            label="Product Description for GIF",
            placeholder="Enter the description to generate images and a GIF from...",
            lines=5
        )
        gif_status_output = gr.Textbox(label="Generation Status", lines=3)
        gif_output = gr.Image(label="Generated GIF", type="filepath")
        gif_generate_button = gr.Button(value="Generate GIF")

        gif_generate_button.click(
            generate_gif_from_description,
            inputs=[gif_description_input],
            outputs=[gif_status_output, gif_output]
        )

    with gr.Tab("Generate Product Image"):
        gr.Markdown("### Generate Product Images from Keywords")
        
        with gr.Row():
            with gr.Column():
                product_name_input = gr.Textbox(
                    label="Product Name", 
                    placeholder="Enter product name (e.g., Wireless Gaming Mouse)",
                    lines=1
                )
                product_keywords = gr.Textbox(
                    label="Additional Keywords (optional)",
                    placeholder="gaming, RGB lighting, ergonomic, black",
                    lines=2
                )
                image_style = gr.Radio(
                    choices=["product", "realistic", "artistic", "minimalist", "isometric"],
                    label="Image Style",
                    value="product"
                )
                image_size = gr.Radio(
                    choices=["512x512", "640x384", "384x640", "768x512"],
                    label="Image Size",
                    value="512x512"
                )
                gen_image_btn = gr.Button("Generate Product Image", variant="primary")
            
            with gr.Column():
                image_output = gr.Image(label="Generated Product Image")
                image_status = gr.Textbox(label="Status", interactive=False)
        
        gen_image_btn.click(
            fn=generate_product_image,
            inputs=[product_name_input, product_keywords, image_style, image_size],
            outputs=[image_status, image_output]
        )

    with gr.Tab("Generate Ad Campaign"):
        gr.Markdown("### 🧠 Intelligent Advertising Campaign Generator")
        
        with gr.Row():
            with gr.Column():
                ad_product = gr.Textbox(
                    label="Product/Service", 
                    placeholder="Enter your product or service name",
                    lines=1
                )
                ad_target = gr.Textbox(
                    label="Target Audience", 
                    placeholder="Who is your target audience? (e.g., young professionals)",
                    lines=1
                )
                ad_format = gr.Textbox(
                    label="Advertising Format", 
                    placeholder="Where will this run? (e.g., Instagram, email, billboard)",
                    lines=1
                )
                gen_campaign_btn = gr.Button("Generate Campaign", variant="primary")
            
            with gr.Column():
                campaign_output = gr.Textbox(
                    label="Generated Campaign", 
                    lines=12,
                    interactive=False
                )
        
        # Add audio generation
        with gr.Row():
            voice_choice = gr.Dropdown(
                choices=list(voice_descriptions.keys()),
                label="Voice for Audio",
                value="Aria"
            )
            generate_audio_btn = gr.Button("Generate Audio from Campaign")
            audio_output = gr.Audio(label="Audio Version")
            audio_status = gr.Textbox(label="Audio Status", interactive=False)
        
        # Connect buttons to functions
        gen_campaign_btn.click(
            fn=generate_ad_campaign,
            inputs=[ad_product, ad_target, ad_format],
            outputs=campaign_output
        )
        
        generate_audio_btn.click(
            fn=generate_audio,
            inputs=[campaign_output, voice_choice],
            outputs=[audio_output, audio_status]
        )

    with gr.Tab("Marketing Strategy Recommender"):
        gr.Markdown("### 🚀 Digital Marketing Strategy Recommender for SMEs")
        gr.Markdown("Find the most suitable marketing strategies for your business needs")
        
        with gr.Row():
            with gr.Column():
                industry_input = gr.Dropdown(
                    label="Industry",
                    choices=get_all_industries(),
                    value=get_all_industries()[0] if get_all_industries() else "retail"
                )
                budget_input = gr.Slider(
                    label="Monthly Budget Amount ($)",
                    minimum=500,
                    maximum=10000,
                    value=2000,
                    step=500
                )
                hours_input = gr.Slider(
                    label="Daily Hours Available",
                    minimum=1,
                    maximum=24,
                    value=8,
                    step=1
                )
                tech_input = gr.Slider(
                    label="Technical Skills (1=Beginner, 5=Expert)",
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1
                )
                audience_input = gr.Slider(
                    label="Target Audience Size (1=Small, 5=Large)",
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1
                )
                goal_input = gr.Radio(
                    label="Primary Marketing Goal",
                    choices=[
                        ("Increase Conversion", "conversion"),
                        ("Boost Awareness", "awareness"),
                        ("Generate Leads", "leads"),
                        ("Improve Retention", "retention")
                    ],
                    value="awareness"
                )
                gen_recommendations_btn = gr.Button("🚀 Generate Recommendations", variant="primary")
            
            with gr.Column():
                recommendations_output = gr.Textbox(
                    label="Recommended Strategies",
                    placeholder="Your recommendations will appear here...",
                    lines=20
                )
        
        # Connect the button to the function
        gen_recommendations_btn.click(
            fn=get_marketing_recommendations,
            inputs=[
                industry_input,
                budget_input,
                hours_input,
                tech_input,
                audience_input,
                goal_input
            ],
            outputs=recommendations_output
        )

    with gr.Tab("Product Trend Prediction"):
        gr.Markdown("### 📈 Product Trend Prediction")
        gr.Markdown("Predict sales trends for your product based on various factors")
        
        with gr.Row():
            with gr.Column():
                trend_product_name = gr.Textbox(
                    label="Product Name",
                    placeholder="Enter your product name (e.g., Eco-Friendly Bamboo Toothbrush)"
                )
                trend_category = gr.Textbox(
                    label="Category",
                    placeholder="Enter the product category (e.g., Home & Kitchen)"
                )
                trend_initial_price = gr.Number(
                    label="Initial Price ($)",
                    value=10.0
                )
                trend_marketing_budget = gr.Number(
                    label="Marketing Budget ($)",
                    value=1000.0
                )
                trend_time_period = gr.Number(
                    label="Time Period (weeks)",
                    value=12
                )
                trend_seasonality_factor = gr.Slider(
                    label="Seasonality Factor (0=Low, 1=High)",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.5,
                    step=0.1
                )
                trend_competition_level = gr.Slider(
                    label="Competition Level (0=Low, 1=High)",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.5,
                    step=0.1
                )
                predict_trend_btn = gr.Button("Predict Trend", variant="primary")
            
            with gr.Column():
                trend_chart_output = gr.Image(label="Trend Chart")
                trend_summary_output = gr.Textbox(
                    label="Trend Summary",
                    placeholder="Your trend summary will appear here...",
                    lines=20
                )
        
        # Connect the button to the function
        predict_trend_btn.click(
            fn=predict_product_trend,
            inputs=[
                trend_product_name,
                trend_category,
                trend_initial_price,
                trend_marketing_budget,
                trend_time_period,
                trend_seasonality_factor,
                trend_competition_level
            ],
            outputs=[trend_chart_output, trend_summary_output]
        )

# --- Main Execution ---
if __name__ == "__main__":
    # Add auto-initialization of data here to compensate for removing the Data Preparation tab
    print("Initializing advertising data...")
    try:
        entries = load_advertising_data()
        embeddings = load_or_build_embeddings(entries)
        if embeddings is not None:
            print("Advertising data initialized successfully.")
        else:
            print("Warning: Embeddings could not be built. Some features may be limited.")
    except Exception as e:
        print(f"Error initializing data: {e}")
    
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("generated_gifs", exist_ok=True)
    os.makedirs("generated_images", exist_ok=True)
    
    print("Starting Product Description Generator App...")
    try:
        import PIL
        import imageio
        import transformers
        import datasets
    except ImportError as e:
        print(f"Missing required library: {e.name}. Please install it.")
        print("Run: pip install imageio Pillow requests transformers datasets")
        exit()

    demo.launch()
    print("Gradio App launched. Access it via the provided URL.")