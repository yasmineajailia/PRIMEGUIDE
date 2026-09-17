# Direct test of the image generator module
import os
import sys
import logging
import time
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("direct_test.log")
    ]
)

logger = logging.getLogger("product-ai-hub")

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the image generator
print("Importing image generator...")
try:
    from generators.image_generator import generate_product_image
    print("Successfully imported image_generator")
except Exception as e:
    print(f"Error importing image_generator: {e}")
    sys.exit(1)

def test_image_generation():
    """Test image generation with proper logging"""
    print("\n" + "=" * 80)
    print("TESTING IMAGE GENERATION WITH LOGGING")
    print("=" * 80)
    
    product_name = "Smart Fitness Tracker Watch"
    keywords = "health monitoring, fitness, step counter, heart rate monitor"
    style = "product"
    size = "512x512"
    
    print(f"Generating image for: {product_name}")
    print(f"Keywords: {keywords}")
    print(f"Style: {style}")
    print(f"Size: {size}")
    
    start_time = time.time()
    
    # Call the generator
    status, image_path = generate_product_image(
        product_name=product_name,
        keywords=keywords,
        image_style=style,
        image_size=size
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print(f"RESULT: {'SUCCESS' if image_path else 'FAILED'}")
    print("=" * 80)
    
    print(f"Status: {status}")
    if image_path:
        print(f"Image saved to: {image_path}")
        print(f"Generation took {duration:.2f} seconds")
        
        # Show image paths for testing
        relative_path = image_path.replace('\\', '/')
        if '/' in relative_path:
            relative_path = '/' + '/'.join(relative_path.split('/')[1:])
        
        # Also create a static URL path for backward compatibility
        static_path = '/static' + relative_path
        
        print("\nURL Paths for testing:")
        print(f"Direct path: {relative_path}")
        print(f"Static path: {static_path}")
        
        return True
    else:
        print("Image generation failed.")
        return False

if __name__ == "__main__":
    result = test_image_generation()
    sys.exit(0 if result else 1)
