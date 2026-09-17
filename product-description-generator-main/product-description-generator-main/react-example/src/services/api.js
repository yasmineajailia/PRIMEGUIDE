import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create API service with common configuration
const apiService = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Text Generation API
export const generateProductDescription = async (data) => {
  try {
    const response = await apiService.post('/generate-product-description', {
      product_name: data.product_name,
      keywords: data.keywords || '',
      tone: data.tone || 'Professional',
      model_type: data.model_type || 'default',
    });
    return response.data;
  } catch (error) {
    console.error('Error generating product description:', error);
    throw error;
  }
};

// Audio Generation API
export const generateAudio = async (data) => {
  try {
    const response = await apiService.post('/generate-audio', {
      text: data.text,
      voice_id: data.voice_id || 'Aria',
      style: data.style || 0.5,
    });
    return response.data;
  } catch (error) {
    console.error('Error generating audio:', error);
    throw error;
  }
};

// Get available voices
export const getAvailableVoices = async () => {
  try {
    const response = await apiService.get('/available-voices');
    return response.data.voices;
  } catch (error) {
    console.error('Error getting available voices:', error);
    throw error;
  }
};

// Image Generation API 
export const generateProductImage = async (data) => {
  try {
    const response = await apiService.post('/generate-product-image', {
      product_name: data.product_name,
      keywords: data.keywords || '',
      image_style: data.image_style || 'product',
      image_size: data.image_size || '512x512',
    });
    return response.data;
  } catch (error) {
    console.error('Error generating product image:', error);
    throw error;
  }
};

// Trend Prediction API
export const predictTrend = async (data) => {
  try {
    const response = await apiService.post('/predict-trend', {
      product_name: data.product_name,
      category: data.category,
      target_demographic: data.target_demographic,
      initial_price: parseFloat(data.initial_price),
      marketing_budget: parseFloat(data.marketing_budget),
      time_period: parseInt(data.time_period, 10),
      seasonality_factor: parseFloat(data.seasonality_factor),
      competition_level: parseFloat(data.competition_level),
    });
    return response.data;
  } catch (error) {
    console.error('Error predicting trend:', error);
    throw error;
  }
};

// Utility function to play audio from a URL
export const playAudio = (audioUrl) => {
  try {
    const fullUrl = audioUrl.startsWith('http') ? audioUrl : `${API_URL}${audioUrl}`;
    const audio = new Audio(fullUrl);
    return audio.play();
  } catch (error) {
    console.error('Error playing audio:', error);
    throw error;
  }
};

// Utility function to download a file from a URL
export const downloadFile = (url, filename) => {
  try {
    const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error downloading file:', error);
    throw error;
  }
};

// Utility function to download a file from a URL
export const downloadFile = (url, filename) => {
  try {
    const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error downloading file:', error);
    throw error;
  }
};
  }
};

// Image Generation API
export const generateProductImage = async (data) => {
  try {
    const response = await apiService.post('/generate-product-image', {
      product_name: data.product_name,
      keywords: data.keywords || '',
      image_style: data.image_style || 'product',
      image_size: data.image_size || '512x512',
    });
    return response.data;
  } catch (error) {
    console.error('Error generating product image:', error);
    throw error;
  }
};

// Trend Prediction API
export const predictTrend = async (data) => {
  try {
    const response = await apiService.post('/predict-trend', data);
    return response.data;
  } catch (error) {
    console.error('Error predicting trend:', error);
    throw error;
  }
};

export default {
  generateProductDescription,
  generateAudio,
  getAvailableVoices,
  generateProductImage,
  predictTrend,
};
