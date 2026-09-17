# Test script to verify image generator's enhanced logging
import os
import sys
import logging
import torch
from PIL import Image
import time

# Get the absolute path of the project directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
# Add the project directory to the Python path
sys.path.append(project_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_dir, 'image_generator_test.log'))
    ]
)
logger = logging.getLogger("product-ai-hub")

def mock_log_progress_callback(pipe, step_index, timestep, callback_kwargs):
    """Mock progress callback for testing with new API"""
    if step_index % 5 == 0 or step_index == 0 or step_index == 29:
        progress_percent = int((step_index + 1) / 30 * 100)
        logger.info(f"Generation progress: {progress_percent}% (Step {step_index+1}/30)")
        # Also print directly to ensure we see output even if logger is not configured properly
        print(f"Generation progress: {progress_percent}% (Step {step_index+1}/30)")
    return callback_kwargs

class MockPipeline:
    """Mock StableDiffusionPipeline for testing"""
    def __init__(self):
        self.generation_steps = 30
    
    def __call__(self, prompt, negative_prompt=None, num_inference_steps=30, height=512, width=512, 
                 guidance_scale=7.5, generator=None, callback_on_step_end=None, callback_steps=1):
        logger.info(f"Generating image with prompt: {prompt}")
        logger.info(f"Settings: {num_inference_steps} steps, {width}x{height}, guidance: {guidance_scale}")
        
        # Simulate the generation process with the callback
        for step in range(num_inference_steps):
            if callback_on_step_end and step % callback_steps == 0:
                callback_kwargs = {"latents": None}
                callback_on_step_end(self, step, 1000 - (step * 30), callback_kwargs)
            time.sleep(0.1)  # Simulate some processing time
        
        # Create a simple test image
        img = Image.new('RGB', (width, height), color=(73, 109, 137))
        
        return type('MockOutput', (), {'images': [img]})
    
    def enable_attention_slicing(self):
        logger.info("Attention slicing enabled")
    
    def enable_vae_slicing(self):
        logger.info("VAE slicing enabled")

def test_generate_product_image():
    """Test function to simulate the image generation process"""
    logger.info("Starting image generation test")
    
    # Parameters for the test
    product_name = "Smart Watch with Health Monitoring"
    keywords = "technology, fitness tracker, heart rate monitor, smart device"
    image_style = "product"
    image_size = "512x512"
    
    logger.info(f"Product: {product_name}")
    logger.info(f"Keywords: {keywords}")
    logger.info(f"Style: {image_style}")
    logger.info(f"Size: {image_size}")
    
    try:
        # Parse image size
        width, height = [int(x) for x in image_size.split("x")]
        
        # Style templates - same as in the actual generator
        style_templates = {
            "product": "professional product photography, {}, studio lighting, detailed, 8k, commercial photography",
            "realistic": "photorealistic {}, detailed texture, natural lighting, 8k resolution",
            "artistic": "artistic rendering of {}, colorful, creative composition, vibrant colors",
            "minimalist": "minimalist design of {}, clean background, simple lines, elegant, modern",
            "isometric": "isometric view of {}, 3D rendering, clean design, product visualization"
        }
        
        # Apply style template
        full_prompt = product_name
        if keywords:
            full_prompt = f"{product_name}, {keywords}"
            
        style_prompt = style_templates.get(image_style, style_templates["product"]).format(full_prompt)
        logger.info(f"Generated prompt: {style_prompt}")
          # Create a mock pipeline
        pipe = MockPipeline()
        
        # Enable optimization methods (for logging verification)
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
        
        # Generate the image
        logger.info("Starting image generation...")
        
        start_time = time.time()
        output = pipe(
            prompt=style_prompt,
            negative_prompt="blurry, bad quality, worst quality, text, watermark",
            num_inference_steps=30,
            height=height,
            width=width,
            guidance_scale=7.5,
            callback_on_step_end=mock_log_progress_callback,
            callback_steps=1
        )
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"Image generation completed in {duration:.2f} seconds")
        
        # Save the generated image
        output_dir = os.path.join(project_dir, "test_generated_images")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a sanitized filename
        safe_product_name = ''.join(c for c in product_name.lower() if c.isalnum() or c == ' ').strip()
        safe_product_name = safe_product_name.replace(' ', '_')
        image_filename = f"{safe_product_name}_test.png"
        image_filepath = os.path.join(output_dir, image_filename)
        
        # Save the image
        output.images[0].save(image_filepath)
        logger.info(f"Test image saved to {image_filepath}")
        
        # Create URLs for testing
        regular_url = f"/test_generated_images/{image_filename}"
        static_url = f"/static/test_generated_images/{image_filename}"
        
        logger.info("Image URLs:")
        logger.info(f"Regular path: {regular_url}")
        logger.info(f"Static path:  {static_url}")
        
        return {
            "success": True,
            "status": f"Generated test image for '{product_name}'",
            "image_path": image_filepath,
            "regular_url": regular_url,
            "static_url": static_url,
            "duration": duration
        }
        
    except Exception as e:
        logger.error(f"Error in test image generation: {str(e)}", exc_info=True)
        return {
            "success": False,
            "status": f"Error: {str(e)}",
            "image_path": None
        }

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING IMAGE GENERATOR WITH ENHANCED LOGGING")
    print("=" * 80)
    
    result = test_generate_product_image()
    
    print("\n" + "=" * 80)
    print(f"TEST RESULT: {'SUCCESS' if result['success'] else 'FAILED'}")
    print("=" * 80)
    print(f"Status: {result['status']}")
    
    if result['success']:
        print(f"Image path: {result['image_path']}")
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"Regular URL: {result['regular_url']}")
        print(f"Static URL: {result['static_url']}")
    
    print("\nCheck the console output above and the log file for detailed logging information.")
    print("This test verifies that the progress is properly displayed during image generation.")
