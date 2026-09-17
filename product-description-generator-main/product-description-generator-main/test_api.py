import requests
import time
import sys
import os
import argparse
import webbrowser

def test_description_generation(base_url):
    """Test the product description generation endpoint"""
    endpoint = f"{base_url}/generate-product-description"
    data = {
        "product_name": "Smart Fitness Watch",
        "keywords": "heart rate monitor, step counter, sleep tracking, waterproof",
        "tone": "Enthusiastic"
    }
    
    print("\n📝 Testing Product Description Generation...")
    response = requests.post(endpoint, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Status: {result['status']}")
        print("\nDescription:")
        print("-" * 80)
        print(result["description"])
        print("-" * 80)
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    return response.status_code == 200

def test_image_generation(base_url):
    """Test the product image generation endpoint"""
    endpoint = f"{base_url}/generate-product-image"
    data = {
        "product_name": "Smart Coffee Maker",
        "keywords": "modern, sleek, stainless steel",
        "image_style": "product"
    }
    
    print("\n🖼️ Testing Product Image Generation...")
    response = requests.post(endpoint, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Status: {result['status']}")
        image_url = f"{base_url}{result['image_url']}"
        print(f"Image URL: {image_url}")
        
        # Open the image in browser
        webbrowser.open(image_url)
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    return response.status_code == 200

def test_audio_generation(base_url):
    """Test the audio generation endpoint"""
    # First get available voices
    voices_endpoint = f"{base_url}/available-voices"
    voices_response = requests.get(voices_endpoint)
    
    if voices_response.status_code != 200:
        print(f"❌ Error getting voices: {voices_response.status_code} - {voices_response.text}")
        return False
    
    voices = voices_response.json()["voices"]
    voice_id = list(voices.keys())[0]  # Use the first available voice
    
    # Now generate audio
    endpoint = f"{base_url}/generate-audio"
    data = {
        "text": "Hello! This is a test of the audio generation API. I hope you're having a great day!",
        "voice_id": voice_id,
        "style": 0.5
    }
    
    print(f"\n🔊 Testing Audio Generation with voice: {voice_id}...")
    response = requests.post(endpoint, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Status: {result['status']}")
        audio_url = f"{base_url}{result['audio_url']}"
        print(f"Audio URL: {audio_url}")
        
        # Open the audio in browser
        webbrowser.open(audio_url)
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    return response.status_code == 200

def test_trend_prediction(base_url):
    """Test the trend prediction endpoint"""
    endpoint = f"{base_url}/predict-trend"
    data = {
        "product_name": "Smart Water Bottle",
        "category": "Fitness",
        "target_demographic": "Young Adults",
        "initial_price": 29.99,
        "marketing_budget": 5000,
        "time_period": 30,
        "seasonality_factor": 1.2,
        "competition_level": 0.6
    }
    
    print("\n📈 Testing Trend Prediction...")
    response = requests.post(endpoint, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        data = result["data"]
        print(f"Product: {data['product_name']}")
        print(f"Average Growth: {data['metrics']['average_growth']}")
        print(f"Peak Day: {data['metrics']['peak_day']}")
        print("\nRecommendations:")
        for rec in data["recommendations"]:
            print(f"- {rec}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    return response.status_code == 200

def main():
    parser = argparse.ArgumentParser(description="Test the Product AI Hub API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--test", choices=["all", "description", "image", "audio", "trend"], 
                        default="all", help="Which test to run")
    args = parser.parse_args()
    
    base_url = args.url
    
    # Test API connectivity
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print(f"✅ Connected to API at {base_url}")
            print(f"API Status: {response.json()['status']}")
        else:
            print(f"❌ API responded with status code {response.status_code}")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"❌ Failed to connect to API at {base_url}: {e}")
        print("Make sure the API server is running and the URL is correct.")
        sys.exit(1)
    
    # Run tests based on command line argument
    if args.test == "all" or args.test == "description":
        test_description_generation(base_url)
    
    if args.test == "all" or args.test == "image":
        test_image_generation(base_url)
    
    if args.test == "all" or args.test == "audio":
        test_audio_generation(base_url)
    
    if args.test == "all" or args.test == "trend":
        test_trend_prediction(base_url)
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    main()
