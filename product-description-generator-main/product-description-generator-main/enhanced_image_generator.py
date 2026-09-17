# Updated image generator with improved logging and error handling
import os
import sys
import traceback
import uuid
import torch
import logging
from diffusers import StableDiffusionPipeline
from PIL import Image
import time

# Configure logger
logger = logging.getLogger("product-ai-hub")

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
    logger.info(f"Image style: {image_style}, Image size: {image_size}")
    
    if not product_name:
        logger.error("No product name provided")
        return "Error: Please provide a product name.", None
    
    start_time = time.time()
    
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
        
        logger.info("Loading Stable Diffusion model...")
        
        # Use identical model configuration as in gif_generator.py
        pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            revision="fp16",
            safety_checker=None,
            requires_safety_checker=False,
            cache_dir="D:/HuggingFace"  # Explicit cache directory
        )
        
        logger.info("Model loaded successfully")
        
        # Optimize for CPU usage
        logger.info("Applying CPU optimizations...")
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
        
        # Parse image size
        try:
            width, height = [int(x) for x in image_size.split("x")]
            logger.info(f"Parsed image dimensions: {width}x{height}")
        except ValueError:
            logger.error(f"Invalid image size format: {image_size}")
            return f"Error: Invalid image size format: {image_size}. Expected format: widthxheight", None
        
        # Style enhancement templates
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
        logger.info(f"Final prompt: {style_prompt}")
        
        # Generate with consistent seed
        generator = torch.Generator().manual_seed(42)
          # Define a callback function to log progress
        def log_progress_callback(pipe, step_index, timestep, callback_kwargs):
            if step_index % 5 == 0 or step_index == 0 or step_index == 29:  # Log first, every 5th, and last step
                progress_percent = int((step_index + 1) / 30 * 100)
                logger.info(f"Generation progress: {progress_percent}% (Step {step_index+1}/30)")
            return callback_kwargs
        
        logger.info("Starting image generation...")
        # Generate the image
        image = pipe(
            prompt=style_prompt,
            negative_prompt="blurry, bad quality, worst quality, text, watermark",
            num_inference_steps=30,
            height=height,
            width=width,
            guidance_scale=7.5,
            generator=generator,
            callback_on_step_end=log_progress_callback,
            callback_steps=1  # Ensure callback_steps is not None
        ).images[0]
        
        logger.info("Image generation completed")
        
        # Create directory for generated images
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Ensuring output directory exists: {output_dir}")
        
        # Save the generated image
        safe_product_name = ''.join(c for c in product_name.lower() if c.isalnum() or c == ' ').strip()
        safe_product_name = safe_product_name.replace(' ', '_')
        image_filename = f"{safe_product_name}_{uuid.uuid4()}.png"
        image_filepath = os.path.join(output_dir, image_filename)
        
        image.save(image_filepath)
        
        # Also create a static directory symbolic link if it doesn't exist
        if not os.path.exists("static"):
            os.makedirs("static", exist_ok=True)
        
        if not os.path.exists("static/generated_images"):
            try:
                # Create symbolic link for the static directory
                if os.name == 'nt':  # Windows
                    os.system(f'mklink /J "{os.path.abspath("static/generated_images")}" "{os.path.abspath(output_dir)}"')
                else:  # Unix
                    os.symlink(os.path.abspath(output_dir), os.path.abspath("static/generated_images"))
                logger.info("Created symbolic link for static/generated_images")
            except Exception as e:
                logger.warning(f"Failed to create symbolic link: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Product image saved successfully to {image_filepath}")
        logger.info(f"Image generation took {duration:.2f} seconds")
        
        # Prepare both URL versions
        regular_url = f"/generated_images/{image_filename}"
        static_url = f"/static/generated_images/{image_filename}"
        logger.info(f"Image URLs: Regular: {regular_url}, Static: {static_url}")
        
        return f"Generated product image for '{product_name}' in {duration:.2f} seconds", image_filepath
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error generating product image: {e}")
        logger.error(error_trace)
        error_message = f"Error generating product image: {str(e)}"
        return error_message, None

# Function to test the image generator as a standalone module
def test_generator():
    """Standalone test function for the image generator"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("image_generator_test.log")
        ]
    )
    
    print("=" * 80)
    print("TESTING PRODUCT IMAGE GENERATOR")
    print("=" * 80)
    
    product_name = "Wireless Bluetooth Headphones"
    keywords = "premium, noise-cancelling, comfortable, modern design"
    
    print(f"Generating image for: {product_name}")
    print(f"Keywords: {keywords}")
    
    status, image_path = generate_product_image(product_name, keywords)
    
    print("\n" + "=" * 80)
    print("RESULT:")
    print(f"Status: {status}")
    print(f"Image path: {image_path}")
    
    if image_path:
        print("Image generated successfully!")
        
        # Prepare URLs for both paths
        regular_url = f"/generated_images/{os.path.basename(image_path)}"
        static_url = f"/static/generated_images/{os.path.basename(image_path)}"
        
        print("\nIMAGE ACCESS URLS:")
        print(f"Regular path: {regular_url}")
        print(f"Static path:  {static_url}")
        
        print("\nNote: These URLs can be accessed when running the FastAPI application.")
    else:
        print("Image generation failed.")

# Run the test if this file is executed directly
if __name__ == "__main__":
    test_generator()
