# Image Description API Usage Guide

## Overview

The Product Description Generator includes an API endpoint that can analyze product images and generate detailed, SEO-friendly descriptions automatically.

## API Endpoints

The API provides two endpoints for generating descriptions from images:

1. **`/upload-image`** (Recommended) - The main endpoint for image-to-description generation
2. **`/generate-description-from-image`** (Alternative) - A secondary endpoint that may be available depending on the server configuration

Both endpoints provide the same functionality, but we recommend using `/upload-image` for consistency.

## Using the API

### Via cURL

```bash
curl -X POST "http://127.0.0.1:8000/upload-image" -F "image=@/path/to/your/image.jpg"
```

### Via Python

```python
import requests

# URL of the API endpoint
url = "http://127.0.0.1:8000/upload-image"

# Path to your image file
image_path = "path/to/your/image.jpg"

# Upload the image
with open(image_path, 'rb') as img_file:
    files = {'image': (os.path.basename(image_path), img_file, 'image/jpeg')}
    response = requests.post(url, files=files)

# Check the response
if response.status_code == 200:
    result = response.json()
    print(f"Generated Description: {result['description']}")
else:
    print(f"Error: {response.text}")
```

### Via HTML

You can use the provided HTML client to easily upload images and get descriptions:

1. Open the file `image_description_client.html` in your browser
2. Upload an image using the file picker
3. Select the endpoint you want to use (default is `/upload-image`)
4. Click "Generate Description"
5. View the generated description below

Alternatively, run the Python script `open_client_direct.py` to automatically open the HTML client in your default browser.

## Response Format

The API returns a JSON response with the following structure:

```json
{
  "success": true,
  "description": "🍪 A Sweet Symphony of Cookies & Candies! 🍬\n\nDetailed description here...",
  "status": "Generated description from uploaded image"
}
```

## Error Handling

If an error occurs, the API will return an appropriate HTTP status code along with an error message.

## Note on CORS

The API has CORS enabled for all origins (`*`) which makes it suitable for development. For production use, you should restrict the allowed origins to your specific domain(s).

## Additional Information

For more details on the API, refer to the Swagger documentation at `http://127.0.0.1:8000/docs` when the API server is running.
