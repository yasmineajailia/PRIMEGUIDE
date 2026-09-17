import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AudioGenerator from '../components/AudioGenerator';
import * as apiService from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  getAvailableVoices: jest.fn(),
  generateAudio: jest.fn(),
}));

describe('AudioGenerator Component', () => {
  beforeEach(() => {
    // Setup mocks
    apiService.getAvailableVoices.mockResolvedValue({
      'Aria': 'Bright and expressive female voice',
      'Roger': 'Deep and composed male voice',
    });
    
    apiService.generateAudio.mockResolvedValue({
      success: true,
      audio_url: '/generated_audio/test.mp3',
      status: 'Generated audio for provided text',
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders the audio generator form', async () => {
    render(<AudioGenerator />);
    
    // Component should render with a heading
    expect(screen.getByText('Audio Generator')).toBeInTheDocument();
    
    // Wait for the voices to load
    await waitFor(() => {
      expect(apiService.getAvailableVoices).toHaveBeenCalled();
    });
    
    // Form elements should be present
    expect(screen.getByLabelText(/Text to Convert/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Voice/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Style Intensity/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Audio/i })).toBeInTheDocument();
  });

  test('submits the form and generates audio', async () => {
    render(<AudioGenerator />);
    
    // Wait for the voices to load
    await waitFor(() => {
      expect(apiService.getAvailableVoices).toHaveBeenCalled();
    });
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/Text to Convert/i), {
      target: { value: 'This is a test message for audio generation.' },
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /Generate Audio/i }));
    
    // API should be called with the correct data
    await waitFor(() => {
      expect(apiService.generateAudio).toHaveBeenCalledWith({
        text: 'This is a test message for audio generation.',
        voice_id: 'Aria', // Default voice
        style: 0.5, // Default style
      });
    });
    
    // Audio player should appear after successful generation
    await waitFor(() => {
      expect(screen.getByText('Generated Audio')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Download Audio/i })).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock the API to return an error
    apiService.generateAudio.mockRejectedValue({
      response: { data: { detail: 'Failed to generate audio' } },
    });
    
    render(<AudioGenerator />);
    
    // Wait for the voices to load
    await waitFor(() => {
      expect(apiService.getAvailableVoices).toHaveBeenCalled();
    });
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText(/Text to Convert/i), {
      target: { value: 'This should fail.' },
    });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /Generate Audio/i }));
    
    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText(/Error: Failed to generate audio/i)).toBeInTheDocument();
    });
  });
});
