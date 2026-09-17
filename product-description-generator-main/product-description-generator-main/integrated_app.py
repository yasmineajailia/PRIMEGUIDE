import os
import gradio as gr
import pandas as pd
import numpy as np
import torch
# Make dotenv loading more robust
try:
    from dotenv import load_dotenv
    # Try to load the environment variables
    try:
        load_dotenv()
        print("Environment variables loaded from .env file")
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
        print("Setting API keys manually...")
        # Set API keys manually as fallback
        os.environ["GOOGLE_API_KEY"] = "AIzaSyCNTLe0l7JqN46i0jUn6tDSTxg7sqwKaPg"
        os.environ["ELEVENLABS_API_KEY"] = "sk_226ebbc21f2e57a1f0709191bc71e2f0bffd844ad95e83bb"
except ImportError:
    print("dotenv module not found, setting API keys manually")
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCNTLe0l7JqN46i0jUn6tDSTxg7sqwKaPg"
    os.environ["ELEVENLABS_API_KEY"] = "sk_226ebbc21f2e57a1f0709191bc71e2f0bffd844ad95e83bb"

# Configure APIs if keys are available
try:
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        try:
            gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            print("Google Generative AI configured successfully")
        except Exception as e:
            print(f"Error creating Gemini model: {e}")
            gemini_model = None
    else:
        print("No Google API key found. Ad campaign generation will be disabled.")
        gemini_model = None
except Exception as e:
    print(f"Error configuring Google Generative AI: {e}")
    gemini_model = None

try:
    from elevenlabs import ElevenLabs, VoiceSettings
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        try:
            eleven_client = ElevenLabs(api_key=api_key)
            print("ElevenLabs API configured successfully")
        except Exception as e:
            print(f"Error creating ElevenLabs client: {e}")
            eleven_client = None
    else:
        print("No ElevenLabs API key found. Audio generation will be disabled.")
        eleven_client = None
except Exception as e:
    print(f"Error configuring ElevenLabs: {e}")
    eleven_client = None

from sentence_transformers import SentenceTransformer
import tempfile
import textstat
import webbrowser
from sklearn.metrics.pairwise import cosine_similarity

# Import directly from generator modules instead of app.py
from generators.text_generator import product_desc_generator,generate_with_t5,generate_with_flan_t5
from generators.image_generator import generate_product_image
from generators.gif_generator import generate_gif_from_description
from trainers.t5_trainer import finetune_t5_on_dataset

from trainers.flan_t5_trainer import finetune_flan_t5_on_dataset

# Import utilities from friend's project
from nlp_utils import analyze_text

# Load embedding model for semantic search
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Voice descriptions from friend's code
voice_descriptions = {
    "Aria": "Bright and expressive female voice",
    "Roger": "Deep and composed male voice",
    "Sarah": "Soft and reassuring female voice",
    "Laura": "Warm and enthusiastic female voice",
    # Add more as needed
}

# Create our own setup functions instead of importing them
def setup_text_generation_tab():
    """Set up the text generation tab UI components"""
    with gr.Row():
        with gr.Column():
            product_input = gr.Textbox(
                label="Product Name/Description", 
                placeholder="Enter a product name or brief description (e.g., Wireless Gaming Mouse)",
                lines=2
            )
            gen_btn = gr.Button("Generate Description", variant="primary")
        
        with gr.Column():
            output_text = gr.Textbox(label="Generated Description", lines=10)
    
    gen_btn.click(
        fn=generate_description,
        inputs=product_input,
        outputs=output_text
    )

def setup_image_generation_tab():
    """Set up the image generation from text tab UI components"""
    with gr.Row():
        with gr.Column():
            img_product_input = gr.Textbox(
                label="Product for Image Generation", 
                placeholder="Enter a product name (e.g., Modern Office Chair)",
                lines=1
            )
            img_gen_btn = gr.Button("Generate Image from Description", variant="primary")
        
        with gr.Column():
            output_image = gr.Image(label="Generated Product Image")
            img_status = gr.Textbox(label="Status", interactive=False)
    
    img_gen_btn.click(
        fn=lambda x: generate_product_image(x, "", "product", "512x512"),
        inputs=img_product_input,
        outputs=[img_status, output_image]
    )

# ========== Data and Index Functions ==========

def load_advertising_data():
    """Load advertising campaign data for RAG"""
    try:
        if os.path.exists("entries.csv"):
            return pd.read_csv("entries.csv").to_dict(orient="records")
        else:
            print("Building advertising database...")
            # Import the specific function from main.py
            from main import load_and_process_data
            return load_and_process_data()
    except Exception as e:
        print(f"Error loading advertising data: {e}")
        return []

def load_or_build_embeddings(entries):
    """Load or build embeddings for semantic search"""
    try:
        if os.path.exists("embeddings.npy"):
            embeddings = np.load("embeddings.npy")
            return embeddings
        else:
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
    """Find semantically similar advertising examples using cosine similarity"""
    if embeddings is None or len(entries) == 0:
        return []
        
    query_vector = embed_model.encode([query])[0].reshape(1, -1)
    
    # Calculate cosine similarity
    similarities = cosine_similarity(query_vector, embeddings)[0]
    
    # Get top k indices
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    return [entries[i] for i in top_indices]

# ========== Audio Generation Functions ==========

def generate_audio(text, voice_id, style=0.5):
    """Generate audio from text using ElevenLabs"""
    if not eleven_client:
        return None, "ElevenLabs API key not configured"
    
    try:
        audio = eleven_client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.4, similarity_boost=0.75, style=style
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

# ========== Campaign Generation Function ==========

def generate_ad_campaign(product, target, ad_format):
    """Generate advertising campaign using RAG with Gemini"""
    if not gemini_model:
        return "Google Gemini API key not configured. Please add it to your .env file."
    
    try:
        # Load data and embeddings
        entries = load_advertising_data()
        embeddings = load_or_build_embeddings(entries)
        
        # Find similar examples using sklearn-based search
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

# ========== Gradio Interface ==========

def build_integrated_ui():
    """Build integrated UI with all features"""
    with gr.Blocks(title="Integrated Product Description & Advertising Generator") as demo:
        gr.Markdown("# 🚀 Integrated Product Marketing Suite")
        
        # Call our local setup functions instead of the imported ones
        with gr.Tab("Generate Description"):
            setup_text_generation_tab()
            
        with gr.Tab("Generate from Image"):
            setup_image_generation_tab()
        
        # Product Image Generator tab
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
            
        # GIF Generator tab
        with gr.Tab("Generate GIF"):
            gr.Markdown("### Generate Animated GIFs from Product Descriptions")
            
            with gr.Row():
                with gr.Column():
                    gif_description = gr.Textbox(
                        label="Product Description", 
                        placeholder="Enter a detailed product description",
                        lines=3
                    )
                    gif_style = gr.Radio(
                        choices=["product", "realistic", "artistic", "minimalist", "isometric"],
                        label="GIF Style",
                        value="product"
                    )
                    gif_frames = gr.Slider(
                        minimum=3, maximum=8, value=4, step=1,
                        label="Number of Frames (more frames = longer generation time)"
                    )
                    gif_size = gr.Radio(
                        choices=["384x384", "512x512"],
                        label="GIF Size (larger = longer generation time)",
                        value="384x384"
                    )
                    gen_gif_btn = gr.Button("Generate GIF", variant="primary")
                
                with gr.Column():
                    gif_output = gr.Image(label="Generated GIF")
                    gif_status = gr.Textbox(label="Status", interactive=False)
            
            gen_gif_btn.click(
                fn=generate_gif_from_description,
                inputs=[gif_description, gif_frames, gif_size, gif_style],
                outputs=[gif_status, gif_output]
            )
            
        # Friend's Advertising Campaign Generator tab
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
            
        # Your model fine-tuning tabs
        with gr.TabItem("Fine-tune Models"):
            with gr.Tab("Fine-tune T5"):
                # Placeholder for T5 fine-tuning interface
                gr.Markdown("### T5 Model Fine-tuning")
                t5_dataset_path = gr.Textbox(
                    label="Dataset Path", 
                    placeholder="data/t5_product_description_data.csv",
                    value="data/t5_product_description_data.csv"
                )
                t5_train_button = gr.Button("Fine-tune T5 Model", variant="primary")
                t5_output = gr.Textbox(label="Training Output", interactive=False, lines=6)
                
                t5_train_button.click(
                    fn=lambda x: "T5 fine-tuning placeholder. Please implement in future versions.",
                    inputs=[t5_dataset_path],
                    outputs=[t5_output]
                )
                
            with gr.Tab("Fine-tune FLAN-T5"):
                # Placeholder for FLAN-T5 fine-tuning interface
                gr.Markdown("### FLAN-T5 Model Fine-tuning")
                flan_t5_dataset_path = gr.Textbox(
                    label="Dataset Path", 
                    placeholder="data/t5_product_description_data.csv",
                    value="data/t5_product_description_data.csv"
                )
                flan_t5_train_button = gr.Button("Fine-tune FLAN-T5 Model", variant="primary")
                flan_t5_output = gr.Textbox(label="Training Output", interactive=False, lines=6)
                
                flan_t5_train_button.click(
                    fn=lambda x: "FLAN-T5 fine-tuning placeholder. Please implement in future versions.",
                    inputs=[flan_t5_dataset_path],
                    outputs=[flan_t5_output]
                )
        
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("generated_gifs", exist_ok=True)
    os.makedirs("generated_images", exist_ok=True)
    
    return demo

# Launch the app
if __name__ == "__main__":
    print("Starting Integrated Product Marketing Suite...")
    
    # Create nlp_utils.py if it doesn't exist (simplified version)
    if not os.path.exists("nlp_utils.py"):
        with open("nlp_utils.py", "w") as f:
            f.write("""
def analyze_text(text):
    \"\"\"Analyze text for sentiment, entities, etc.\"\"\"
    # Simplified implementation
    word_count = len(text.split())
    return {
        "word_count": word_count,
        "character_count": len(text),
        "sentence_count": text.count('.') + text.count('!') + text.count('?')
    }
""")
    
    demo = build_integrated_ui()
    demo.launch()