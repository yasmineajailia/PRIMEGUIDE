import requests
import json

# API URL
api_url = "http://127.0.0.1:8000"

def check_api_status():
    """Check if the API is running and if the image generation endpoint is available"""
    try:
        # Make a request to the root endpoint
        print(f"Checking API status at {api_url}")
        response = requests.get(api_url)
        
        # Check response
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Status: {data['status']}")
            print(f"API Message: {data['message']}")
            
            # Check if the image generation endpoint is listed
            endpoints = data.get('endpoints', {})
            if "POST /generate-product-image" in endpoints:
                print(f"✅ Image generator endpoint is available: {endpoints['POST /generate-product-image']}")
                return True
            else:
                print("❌ Image generator endpoint is not listed in available endpoints")
                print(f"Available endpoints: {json.dumps(endpoints, indent=2)}")
                return False
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Checking Product Image Generator API Status...")
    check_api_status()
