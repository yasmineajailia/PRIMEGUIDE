import requests
import json
import time
import os
import webbrowser

# API URL
api_url = "http://127.0.0.1:8000"

# Test image generation and access through both paths
def test_static_path_access():
    """Test image generation and accessing the image through both /generated_images and /static/generated_images paths"""
    try:
        # Data for the request
        payload = {
            "product_name": "Modern Glass Water Bottle",
            "keywords": "eco-friendly, sustainable, sleek design",
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
            if 'static_image_url' in result:
                print(f"Static Image URL: {result['static_image_url']}")
            print(f"Status: {result['status']}")
            
            # Extract filename from the URL
            filename = result['image_url'].split('/')[-1]
            
            # Test both URL paths
            url_paths = [
                # Original path
                f"{api_url}{result['image_url']}",
                # New static path from API response (if available)
                f"{api_url}{result.get('static_image_url', '')}" if 'static_image_url' in result else None,
                # Manually constructed static path
                f"{api_url}/static/generated_images/{filename}"
            ]
            
            # Filter out None values
            url_paths = [url for url in url_paths if url]
            
            # Test each URL path
            results = []
            for url in url_paths:
                print(f"\nTesting URL: {url}")
                img_response = requests.get(url)
                status = img_response.status_code
                print(f"Status code: {status}")
                
                results.append({
                    "url": url,
                    "status_code": status,
                    "accessible": status == 200
                })
            
            # Create a simple HTML file to test embedding the images
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Image Path Test</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    h1 { color: #333; }
                    .test-result { margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                    .success { background-color: #e6ffe6; }
                    .failure { background-color: #ffe6e6; }
                    img { max-width: 100%; border: 1px solid #ddd; }
                    .status { font-weight: bold; }
                    .success .status { color: green; }
                    .failure .status { color: red; }
                </style>
            </head>
            <body>
                <h1>Image Path Access Test</h1>
            """
            
            for result in results:
                status_class = "success" if result["accessible"] else "failure"
                status_text = "SUCCESS" if result["accessible"] else "FAILED"
                
                html_content += f"""
                <div class="test-result {status_class}">
                    <h2>Path Test: <span class="status">{status_text}</span></h2>
                    <p><strong>URL:</strong> {result["url"]}</p>
                    <p><strong>Status Code:</strong> {result["status_code"]}</p>
                    <div class="image-container">
                        <h3>Image Preview:</h3>
                        <img src="{result["url"]}" alt="Product Image" onerror="this.alt='Image failed to load'; this.style.border='2px solid red';">
                    </div>
                </div>
                """
            
            html_content += """
            </body>
            </html>
            """
            
            # Write the HTML file
            test_html_path = os.path.abspath("static_path_test.html")
            with open(test_html_path, "w") as f:
                f.write(html_content)
            
            print(f"\nCreated HTML test page: {test_html_path}")
            # Open the HTML file in browser for visual confirmation
            webbrowser.open(f"file://{test_html_path}")
            
            # Print summary
            print("\nTest Summary:")
            for result in results:
                status = "✅ ACCESSIBLE" if result["accessible"] else "❌ NOT ACCESSIBLE"
                print(f"{status}: {result['url']}")
            
            return all(result["accessible"] for result in results)
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Static Path Access for Images...")
    success = test_static_path_access()
    print(f"\nOverall test {'succeeded' if success else 'failed'}.")
