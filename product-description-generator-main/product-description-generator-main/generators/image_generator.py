import traceback
import base64
from io import BytesIO
import requests
import json
import os
import torch
import uuid
from diffusers import StableDiffusionPipeline
from PIL import Image
import logging

# Get logger
logger = logging.getLogger("product-ai-hub")

def image_desc_generator(product_image):
    """
    Generates a product description based purely on an uploaded image using Gemini API.
    """
    logger.info("Generating description from image...")
    if product_image is None:
        return "Error: Please upload an image."

    try:
        buffered = BytesIO()
        product_image = product_image.convert("RGB")
        product_image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        gemini_api_key = "AIzaSyCtJCqSj_4mzX_-l9NH8OZMuTG7xVzEX48"
        model_name = "gemini-1.5-flash"
        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
        
        prompt_parts = [
            {"text": "Analyze the following product image and generate a creative, engaging, and SEO-friendly multi-paragraph product description with emojis based solely on the visual features. Use a friendly, informative tone."},
            {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}},
            {"text": "\n\nGENERATED DESCRIPTION:"}
        ]
        
        payload = {"contents": [{"parts": prompt_parts}]}
        headers = {"Content-Type": "application/json"}

        logger.info("Sending image and prompt to generation service...")
        response = requests.post(gemini_api_url, json=payload, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error from generation service: {response.status_code} - {response.text}")
            return f"Error: Generation service returned status code {response.status_code}. Please check API key and configuration."

        try:
            response_data = response.json()
            if response_data and 'candidates' in response_data and len(response_data['candidates']) > 0 and 'content' in response_data['candidates'][0] and 'parts' in response_data['candidates'][0]['content'] and len(response_data['candidates'][0]['content']['parts']) > 0 and 'text' in response_data['candidates'][0]['content']['parts'][0]:
                generated_description = response_data['candidates'][0]['content']['parts'][0]['text']
                logger.info("Description generated successfully from image.")
            elif response_data and 'promptFeedback' in response_data and 'blockReason' in response_data['promptFeedback']:
                block_reason = response_data['promptFeedback']['blockReason']
                logger.warning(f"Generation blocked by safety settings: {block_reason}")
                generated_description = f"Error: Request blocked due to {block_reason}"
            else:
                logger.error(f"Unexpected response structure from generation service: {response_data}")
                generated_description = "Error: Unexpected response structure from generation service."
            
            return generated_description
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON response: {response.text}")
            return f"Error: Could not decode JSON response from generation service."
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during API request: {e}")
            return f"Error: Network error during request to generation service."
        except Exception as e:
            logger.error(f"Unexpected error in image_desc_generator: {e}", exc_info=True)
            return "Error: An unexpected error occurred while generating the description."
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return "Error: An unexpected error occurred."

def generate_product_image(product_name, keywords="", image_style="product", image_size="512x512"):
    """
    Generates a product image from a product name and optional keywords.
    
    Args:
        product_name (str): The name of the product to generate an image for
        keywords (str): Additional keywords to guide the image generation
        image_style (str): The style of image to generate (product, realistic, artistic, etc.)
        image_size (str): The size of the image in format "widthxheight"
        
    Returns:
        tuple: (status_message, image_path)
    """
    logger.info(f"Generating product image for: '{product_name}' with keywords: '{keywords}'")
    
    if not product_name:
        return "Error: Please provide a product name.", None
    
    try:
        # Set environment variables to force CPU and manage memory
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        torch.set_default_device("cpu")
        
        # Set Hugging Face cache directory to D: drive
        os.environ["HF_HOME"] = "D:/HuggingFace"
        os.environ["TRANSFORMERS_CACHE"] = "D:/HuggingFace/transformers"
        os.environ["HF_DATASETS_CACHE"] = "D:/HuggingFace/datasets"
        
        # Create cache directories if they don't exist
        os.makedirs("D:/HuggingFace", exist_ok=True)
        os.makedirs("D:/HuggingFace/transformers", exist_ok=True)
        os.makedirs("D:/HuggingFace/datasets", exist_ok=True)
        
        logger.info("Loading Stable Diffusion model (using same model as GIF generator)...")
        
        # Use identical model configuration as in gif_generator.py
        pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            revision="fp16",
            safety_checker=None,
            requires_safety_checker=False,
            cache_dir="D:/HuggingFace"  # Explicit cache directory
        )
        
        # Optimize for CPU usage - same optimizations as gif_generator
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
        
        # Parse image size
        width, height = [int(x) for x in image_size.split("x")]
        
        # Style enhancement templates - same as gif_generator for consistency
        style_templates = {
            "product": "professional product photography, {}, studio lighting, detailed, 8k, commercial photography",
            "realistic": "photorealistic {}, detailed texture, natural lighting, 8k resolution",
            "artistic": "artistic rendering of {}, colorful, creative composition, vibrant colors",
            "minimalist": "minimalist design of {}, clean background, simple lines, elegant, modern",
            "isometric": "isometric view of {}, 3D rendering, clean design, product visualization"
        }
          # Apply style template with product name and keywords
        full_prompt = product_name
        if keywords:
            full_prompt = f"{product_name}, {keywords}"
            
        style_prompt = style_templates.get(image_style, style_templates["product"]).format(full_prompt)
        
        # Generate with consistent seed
        generator = torch.Generator().manual_seed(42)  # Same seed as base GIF image
        
        logger.info(f"Generating image with prompt: {style_prompt}")
        
        # Define a callback function to log progress using the new callback API
        def log_progress_callback(pipe, step_index, timestep, callback_kwargs):
            if step_index % 5 == 0 or step_index == 0 or step_index == 29:  # Log first, every 5th, and last step
                progress_percent = int((step_index + 1) / 30 * 100)
                logger.info(f"Generation progress: {progress_percent}% (Step {step_index+1}/30)")
            return callback_kwargs
        
        # Generate the image with the same quality settings as gif_generator base image
        image = pipe(
            prompt=style_prompt,
            negative_prompt="blurry, bad quality, worst quality, text, watermark",
            num_inference_steps=30,  # Same as GIF base image for quality
            height=height,
            width=width,
            guidance_scale=7.5,  # Same as GIF generator
            generator=generator,
            callback_on_step_end=log_progress_callback,
            callback_steps=1  # Ensure callback_steps is not None
        ).images[0]
        
        # Create directory for generated images
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the generated image
        safe_product_name = ''.join(c for c in product_name.lower() if c.isalnum() or c == ' ').strip()
        safe_product_name = safe_product_name.replace(' ', '_')
        image_filename = f"{safe_product_name}_{uuid.uuid4()}.png"
        image_filepath = os.path.join(output_dir, image_filename)
        image.save(image_filepath)
        
        logger.info(f"Product image saved successfully to {image_filepath}")
        return f"Generated product image for '{product_name}'", image_filepath
    
    except Exception as e:
        logger.error(f"Error generating product image: {e}", exc_info=True)
        error_message = f"Error generating product image: {e}"
        return error_message, None
