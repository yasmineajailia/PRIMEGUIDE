import requests
import os
from PIL import Image
import io

# Base URL of the API
base_url = "http://127.0.0.1:8000"

def test_image_description():
    """Test the image description generation endpoint"""
    try:
        # Find a sample image file (you can replace this with an actual image path)
        image_path = None
        image_dir = "d:\\PI\\product-description-generator-main\\product-description-generator-main\\generated_images"
        
        if os.path.exists(image_dir):
            files = os.listdir(image_dir)
            image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
            if image_files:
                image_path = os.path.join(image_dir, image_files[0])
        
        if not image_path:
            print("No sample image found. Creating a dummy image...")
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color=(73, 109, 137))
            
            # Save to a temporary file
            image_path = "d:\\PI\\product-description-generator-main\\test_image.jpg"
            img.save(image_path)
        
        print(f"Using image: {image_path}")
        
        # Try both endpoints
        endpoints = ["/generate-description-from-image", "/upload-image"]
        
        for endpoint in endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            # Upload image to API
            with open(image_path, 'rb') as img_file:
                files = {'image': (os.path.basename(image_path), img_file, 'image/jpeg')}
                response = requests.post(f"{base_url}{endpoint}", files=files)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Testing Image Description Generation...")
    test_image_description()
