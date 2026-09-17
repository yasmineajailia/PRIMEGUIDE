# Exporting Models to a Different React Application

This guide explains how to export the AI models from this project to use in a different React application.

## Option 1: API Integration (Recommended)

The simplest way to integrate the models with your React application is through API calls. The `export_api.py` script creates a lightweight API server that exposes only the core model functionality needed for most applications.

### Step 1: Start the API Server

Run the `run_export_api.bat` script to start the API server:

```bash
# Windows
.\run_export_api.bat

# Mac/Linux
bash run_export_api.sh  # If needed, create this script similarly to run_export_api.bat
```

This will start a FastAPI server on port 8000 with the following endpoints:

- `POST /generate-product-description` - Text generation
- `POST /generate-product-image` - Image generation
- `POST /generate-product-gif` - GIF generation
- `POST /generate-description-from-image` - Image-to-text description generation

### Step 2: Integrate with Your React Application

In your React application, you can make API calls to these endpoints. Here are examples using fetch:

#### Text Generation

```javascript
const generateDescription = async (productName, keywords, tone) => {
  try {
    const response = await fetch('http://localhost:8000/generate-product-description', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_name: productName,
        keywords: keywords,
        tone: tone,
        model_type: 'default'  // or 't5' or 'flan-t5'
      }),
    });
    
    if (!response.ok) throw new Error('Failed to generate description');
    const data = await response.json();
    return data.description;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

#### Image Generation

```javascript
const generateImage = async (productName, keywords, style) => {
  try {
    const response = await fetch('http://localhost:8000/generate-product-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_name: productName,
        keywords: keywords,
        image_style: style || 'product',
        image_size: '512x512'
      }),
    });
    
    if (!response.ok) throw new Error('Failed to generate image');
    const data = await response.json();
    
    if (data.success) {
      // Return URL to the generated image
      return `http://localhost:8000${data.image_url}`;
    } else {
      throw new Error(data.status);
    }
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

#### GIF Generation

```javascript
const generateGif = async (description, frames, style) => {
  try {
    const response = await fetch('http://localhost:8000/generate-product-gif', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description_text: description,
        num_frames: frames || 6,
        style: style || 'product',
        image_size: '512x512'
      }),
    });
    
    if (!response.ok) throw new Error('Failed to generate GIF');
    const data = await response.json();
    
    if (data.success) {
      // Return URL to the generated GIF
      return `http://localhost:8000${data.gif_url}`;
    } else {
      throw new Error(data.status);
    }
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

#### Image-to-Text Description Generation

```javascript
const generateDescriptionFromImage = async (imageFile) => {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch('http://localhost:8000/generate-description-from-image', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Failed to generate description from image');
    const data = await response.json();
    return data.description;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

### Step 3: Create React Components

Create React components that use these functions. Here's a simple example:

```jsx
import React, { useState } from 'react';

function ProductDescriptionGenerator() {
  const [productName, setProductName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const result = await generateDescription(productName, keywords, 'Professional');
      setDescription(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Product Description Generator</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Product Name:
            <input 
              type="text" 
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              required
            />
          </label>
        </div>
        <div>
          <label>
            Keywords (optional):
            <input 
              type="text" 
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Description'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
      
      {description && (
        <div>
          <h3>Generated Description:</h3>
          <div className="description">{description}</div>
        </div>
      )}
    </div>
  );
}
```

## Option 2: Package Models and API Together

If you want to distribute your application with the models included:

1. Create a production build of your React application
2. Bundle the Python API with prepackaged models
3. Use a solution like Electron to create a desktop application with both the React frontend and Python API

## Option 3: Export Models to JavaScript (Advanced)

For certain models, you could convert them to formats like ONNX.js or TensorFlow.js, but this is complex and not all models support this approach. This is recommended only for advanced users with specific performance requirements.

## API Specifications

### POST /generate-product-description

Generate a product description using AI.

**Request Body:**
```json
{
  "product_name": "Wireless Gaming Mouse",
  "keywords": "ergonomic, RGB, gaming, lightweight",
  "tone": "Professional",
  "model_type": "default"
}
```

**Response:**
```json
{
  "success": true,
  "description": "Generated product description text..."
}
```

### POST /generate-product-image

Generate a product image using AI.

**Request Body:**
```json
{
  "product_name": "Wireless Gaming Mouse",
  "keywords": "ergonomic, RGB",
  "image_style": "product",
  "image_size": "512x512"
}
```

**Response:**
```json
{
  "success": true,
  "status": "Generated product image for 'Wireless Gaming Mouse'",
  "image_url": "/static/wireless_gaming_mouse_1234.png",
  "local_path": "generated_images/wireless_gaming_mouse_1234.png"
}
```

### POST /generate-product-gif

Generate an animated product GIF using AI.

**Request Body:**
```json
{
  "description_text": "A wireless gaming mouse with RGB lighting and ergonomic design",
  "num_frames": 6,
  "image_size": "512x512",
  "style": "product"
}
```

**Response:**
```json
{
  "success": true,
  "status": "GIF generated successfully",
  "gif_url": "/static-gifs/sd_mini_gif_1234.gif",
  "local_path": "generated_gifs/sd_mini_gif_1234.gif"
}
```

### POST /generate-description-from-image

Generate a product description based on an uploaded product image.

**Request Body:**
- Form data with an `image` field containing the image file

**Response:**
```json
{
  "success": true,
  "description": "Generated product description text from the image..."
}
```
