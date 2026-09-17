import requests
import json

# API URL
api_url = "http://127.0.0.1:8000"

# Test image generation endpoint
def test_image_generation():
    """Test the image generation endpoint"""
    try:
        # Data for the request
        payload = {
            "product_name": "Ergonomic Blue Coffee Mug",
            "keywords": "ceramic, modern design, comfortable handle",
            "image_style": "product",
            "image_size": "512x512"
        }
        
        # Make the request
        print(f"Sending request to {api_url}/generate-product-image")
        response = requests.post(f"{api_url}/generate-product-image", json=payload)
        
        # Check response
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Image URL: {result['image_url']}")
            print(f"Status: {result['status']}")
              # Try to access the image
            image_url = f"{api_url}{result['image_url']}"
            print(f"Full image URL: {image_url}")
            img_response = requests.get(image_url)
            print(f"Image access status code: {img_response.status_code}")
            
            # Try static URL if available
            if 'static_image_url' in result:
                static_image_url = f"{api_url}{result['static_image_url']}"
                print(f"Full static image URL: {static_image_url}")
                static_img_response = requests.get(static_image_url)
                print(f"Static image access status code: {static_img_response.status_code}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Product Image Generation API...")
    test_image_generation()
