# Product Description Generator with React Integration

This project integrates Python-based AI models with a React frontend to provide a comprehensive suite of tools for product marketing:

- **Product Trend Prediction**: AI-powered market performance predictions
- **Product Description Generation**: AI-generated product descriptions with different model options
- **Product Image Generation**: AI-generated product images with various style options
- **Animated GIF Generation**: AI-generated product animations from descriptions

## System Requirements

- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher
- At least 8GB of RAM for model inference

## Setup Instructions

### 1. Installing Python Dependencies

```bash
# Create a Python virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Installing React Dependencies

```bash
# Navigate to the React project directory
cd react-example

# Install npm dependencies
npm install
```

## Running the Application

### Option 1: Using the convenience script (Windows)

Run the provided batch script to start both the API server and React application at once:

```bash
run_integrated_app.bat
```

This will:
- Start the FastAPI server on port 8000
- Start the React development server on port 3000
- Open the React application in your default web browser

### Option 2: Starting servers manually

**Step 1**: Start the FastAPI server
```bash
python api.py
```

**Step 2**: Start the React development server
```bash
cd react-example
npm start
```

The React application will automatically open in your default browser. If it doesn't, navigate to [http://localhost:3000](http://localhost:3000).

## Using the Application

1. **Trend Prediction**: Enter product details to get sales trend predictions
2. **Product Descriptions**: Generate marketing copy with different AI models
3. **Product Images**: Create product images in various styles
4. **Animated GIFs**: Generate animated product showcases

## API Documentation

The API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running.

## Architecture Overview

- **Backend**: FastAPI server exposing AI models through RESTful endpoints
- **Frontend**: React application with responsive UI components
- **Models**:
  - Text generation models (Default API, T5, FLAN-T5)
  - Image generation (Stable Diffusion)
  - GIF generation (Stable Diffusion with animation)
  - Trend prediction and marketing recommendation systems

## Known Limitations

- Image and GIF generation is CPU-intensive and may be slow without GPU acceleration
- Large model downloads may occur on first use if models aren't cached

## Troubleshooting

- If you encounter errors related to model downloads, ensure your internet connection is stable
- For model memory issues, try using smaller image sizes or fewer GIF frames
- Check the console logs for detailed error messages
