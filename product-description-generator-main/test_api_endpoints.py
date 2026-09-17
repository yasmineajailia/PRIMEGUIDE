import requests
import json

# Base URL of the API
base_url = "http://127.0.0.1:8000"

# Test the root endpoint (GET request)
def test_root():
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Test the product description endpoint (POST request)
def test_description():
    try:
        payload = {
            "product_name": "Ergonomic Office Chair",
            "keywords": "comfort, adjustable, lumbar support",
            "tone": "Professional"
        }
        response = requests.post(f"{base_url}/generate-product-description", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Testing API Root Endpoint...")
    test_root()
    
    print("\nTesting Product Description Generation...")
    test_description()
