import requests
import time
import os

def test_image_generation_with_progress():
    """Test the image generation endpoint and observe the enhanced logging in the terminal"""
    print("=" * 80)
    print("TESTING IMAGE GENERATION WITH ENHANCED LOGGING")
    print("=" * 80)
    print("\nThis script will send a request to generate an image.")
    print("You should see detailed progress in the FastAPI terminal window.")
    print("The URL with both regular and static paths will be displayed here.\n")
    
    # API URL
    api_url = "http://127.0.0.1:8000"
    
    # Data for the request
    payload = {
        "product_name": "Smart Coffee Mug with Temperature Control",
        "keywords": "technology, smart gadget, kitchen tech, coffee lover",
        "image_style": "product",
        "image_size": "512x512"
    }
    
    try:
        start_time = time.time()
        print(f"Sending request to {api_url}/generate-product-image")
        print(f"Product: {payload['product_name']}")
        print(f"Keywords: {payload['keywords']}")
        print(f"Image style: {payload['image_style']}")
        
        # Make the request
        response = requests.post(f"{api_url}/generate-product-image", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            end_time = time.time()
            duration = end_time - start_time
            
            print("\n" + "=" * 80)
            print(f"IMAGE GENERATION SUCCESSFUL! (Took {duration:.2f} seconds)")
            print("=" * 80)
            print(f"Success: {result['success']}")
            print(f"Status: {result['status']}")
            
            # Display image URLs
            regular_url = f"{api_url}{result['image_url']}"
            static_url = f"{api_url}{result.get('static_image_url', '/static' + result['image_url'])}"
            
            print("\nIMAGE ACCESS URLS:")
            print(f"Regular path: {regular_url}")
            print(f"Static path:  {static_url}")
            
            # Check if images are accessible
            regular_response = requests.get(regular_url)
            static_response = requests.get(static_url)
            
            print("\nACCESSIBILITY CHECK:")
            print(f"Regular path: {'✅ Accessible' if regular_response.status_code == 200 else '❌ Not accessible'} (Status: {regular_response.status_code})")
            print(f"Static path:  {'✅ Accessible' if static_response.status_code == 200 else '❌ Not accessible'} (Status: {static_response.status_code})")
            
            # Generate HTML to view the images
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Generated Image Test</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1, h2 {{ color: #333; }}
                    .image-container {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    img {{ max-width: 100%; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <h1>Generated Product Image Test</h1>
                <p><strong>Product:</strong> {payload['product_name']}</p>
                <p><strong>Keywords:</strong> {payload['keywords']}</p>
                
                <div class="image-container">
                    <h2>Regular Path Image</h2>
                    <p><code>{regular_url}</code></p>
                    <img src="{regular_url}" alt="Product Image" onerror="this.alt='Image failed to load'; this.style.border='2px solid red';">
                </div>
                
                <div class="image-container">
                    <h2>Static Path Image</h2>
                    <p><code>{static_url}</code></p>
                    <img src="{static_url}" alt="Product Image" onerror="this.alt='Image failed to load'; this.style.border='2px solid red';">
                </div>
            </body>
            </html>
            """
            
            # Write HTML file
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_image_test.html")
            with open(html_path, "w") as f:
                f.write(html_content)
            
            print(f"\nTest HTML page created: {html_path}")
            print(f"Open this file in your browser to view the generated images")
            
            # Try to open the HTML file
            try:
                os.startfile(html_path)
            except:
                print("Could not automatically open the HTML file. Please open it manually.")
            
            return True
            
        else:
            print(f"\nERROR: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_image_generation_with_progress()
