# Integrating API Services with React

This guide explains how to use the audio and text generation services from the Product AI Hub API in your React application.

## Getting Started

1. Ensure the FastAPI backend is running:
   ```powershell
   cd d:\PI\product-description-generator-main\product-description-generator-main
   python fastapi_app.py
   ```
   
   The API should be running on http://localhost:8000

2. Start your React application:
   ```powershell
   cd d:\PI\product-description-generator-main\product-description-generator-main\react-example
   npm start
   ```

## API Integration Components

The integration consists of:

1. **API Service** (`src/services/api.js`): Contains methods for communicating with the FastAPI backend
2. **UI Components**: React components that use the API services

## Available API Services

### Text Generation

```javascript
import { generateProductDescription } from '../services/api';

// Inside your component:
const handleGenerateDescription = async () => {
  try {
    const result = await generateProductDescription({
      product_name: 'Smart Watch',
      keywords: 'fitness, heart rate, water resistant',
      tone: 'Enthusiastic'
    });
    
    if (result.success) {
      // Use result.description
      console.log(result.description);
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Audio Generation

```javascript
import { generateAudio, getAvailableVoices } from '../services/api';

// Get available voices
const fetchVoices = async () => {
  const voices = await getAvailableVoices();
  // voices is an object with voice IDs as keys and descriptions as values
};

// Generate audio
const handleGenerateAudio = async () => {
  try {
    const result = await generateAudio({
      text: 'This is the text to convert to speech',
      voice_id: 'Aria',
      style: 0.5
    });
    
    if (result.success) {
      // Audio URL is available at result.audio_url
      // Play or download the audio
      const audioPlayer = new Audio(`http://localhost:8000${result.audio_url}`);
      audioPlayer.play();
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Image Generation

```javascript
import { generateProductImage } from '../services/api';

// Generate product image
const handleGenerateImage = async () => {
  try {
    const result = await generateProductImage({
      product_name: 'Eco-friendly Water Bottle',
      keywords: 'stainless steel, vacuum insulated',
      image_style: 'product',
      image_size: '512x512'
    });
    
    if (result.success) {
      // Image URL is available at result.image_url
      const imageUrl = `http://localhost:8000${result.image_url}`;
      // Use the image URL in your component
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Trend Prediction

```javascript
import { predictTrend } from '../services/api';

// Predict product trend
const handlePredictTrend = async () => {
  try {
    const result = await predictTrend({
      product_name: 'Smart Water Bottle',
      category: 'Fitness',
      target_demographic: 'Young Adults',
      initial_price: 29.99,
      marketing_budget: 5000,
      time_period: 30,
      seasonality_factor: 1.2,
      competition_level: 0.6
    });
    
    if (result.success) {
      // Trend data is available at result.data
      const trendData = result.data;
      // Use the trend data in your component
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

## Error Handling

All API service methods throw errors if the request fails. You should always wrap API calls in try/catch blocks and provide appropriate error handling.

## CORS Considerations

The FastAPI backend has CORS enabled for localhost development. If you deploy the API to a different domain, you'll need to update the CORS settings in the FastAPI app.

## Authentication

This example does not include authentication. For production use, you should implement proper authentication and authorization.
