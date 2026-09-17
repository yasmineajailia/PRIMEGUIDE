import { generateAudio, getAvailableVoices, playAudio, downloadFile } from '../services/api';
import axios from 'axios';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: jest.fn(),
    get: jest.fn(),
  })),
}));

describe('API Service', () => {
  let mockAxiosInstance;
  
  beforeEach(() => {
    // Get the mock axios instance created by the service
    mockAxiosInstance = axios.create();
    
    // Reset mocks
    jest.clearAllMocks();
  });
  
  describe('getAvailableVoices', () => {
    test('fetches available voices correctly', async () => {
      // Setup mock response
      const mockResponse = {
        data: {
          voices: {
            'Aria': 'Bright and expressive female voice',
            'Roger': 'Deep and composed male voice',
          },
        },
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      // Call the function
      const result = await getAvailableVoices();
      
      // Check axios was called correctly
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/available-voices');
      
      // Check the result
      expect(result).toEqual(mockResponse.data.voices);
    });
    
    test('handles errors correctly', async () => {
      // Setup mock error
      const mockError = new Error('Network error');
      mockAxiosInstance.get.mockRejectedValue(mockError);
      
      // Call the function and expect it to throw
      await expect(getAvailableVoices()).rejects.toThrow('Network error');
      
      // Check axios was called correctly
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/available-voices');
    });
  });
  
  describe('generateAudio', () => {
    test('generates audio correctly', async () => {
      // Setup mock response
      const mockResponse = {
        data: {
          success: true,
          audio_url: '/generated_audio/test.mp3',
          status: 'Generated audio for provided text',
        },
      };
      
      mockAxiosInstance.post.mockResolvedValue(mockResponse);
      
      // Call the function
      const result = await generateAudio({
        text: 'Test text',
        voice_id: 'Aria',
        style: 0.5,
      });
      
      // Check axios was called correctly
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/generate-audio', {
        text: 'Test text',
        voice_id: 'Aria',
        style: 0.5,
      });
      
      // Check the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('handles errors correctly', async () => {
      // Setup mock error
      const mockError = new Error('Server error');
      mockAxiosInstance.post.mockRejectedValue(mockError);
      
      // Call the function and expect it to throw
      await expect(generateAudio({
        text: 'Test text',
      })).rejects.toThrow('Server error');
      
      // Check axios was called correctly
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/generate-audio', {
        text: 'Test text',
        voice_id: 'Aria',
        style: 0.5,
      });
    });
  });
});
