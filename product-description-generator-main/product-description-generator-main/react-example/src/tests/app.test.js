import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  test('renders the application header', () => {
    render(<App />);
    
    // App header should be present
    expect(screen.getByText('Product AI Hub')).toBeInTheDocument();
    expect(screen.getByText('AI-powered tools for product management and marketing')).toBeInTheDocument();
  });
  
  test('shows the Trend Prediction tab by default', () => {
    render(<App />);
    
    // Trend Prediction tab should be active by default
    const trendTab = screen.getByRole('button', { name: /Trend Prediction/i });
    expect(trendTab).toHaveClass('border-indigo-500');
    
    // ProductTrendForm should be visible
    // (Note: This assumes ProductTrendForm has some identifiable element)
    // This might need adjustment based on how ProductTrendForm is structured
    expect(document.querySelector('.max-w-7xl')).toBeInTheDocument();
  });
  
  test('navigates to Audio Generator tab when clicked', () => {
    render(<App />);
    
    // Click on the Audio Generator tab
    fireEvent.click(screen.getByRole('button', { name: /Audio Generator/i }));
    
    // Audio Generator tab should now be active
    const audioTab = screen.getByRole('button', { name: /Audio Generator/i });
    expect(audioTab).toHaveClass('border-indigo-500');
    
    // Audio Generator component should be visible
    expect(screen.getByText('Audio Generator')).toBeInTheDocument();
    
    // Form elements from AudioGenerator should be present
    expect(screen.getByLabelText(/Text to Convert/i)).toBeInTheDocument();
  });
  
  test('navigates back to Trend Prediction tab when clicked', () => {
    render(<App />);
    
    // First navigate to Audio Generator
    fireEvent.click(screen.getByRole('button', { name: /Audio Generator/i }));
    
    // Then navigate back to Trend Prediction
    fireEvent.click(screen.getByRole('button', { name: /Trend Prediction/i }));
    
    // Trend Prediction tab should now be active
    const trendTab = screen.getByRole('button', { name: /Trend Prediction/i });
    expect(trendTab).toHaveClass('border-indigo-500');
    
    // Audio Generator should no longer be visible
    expect(screen.queryByText('Text to Convert')).not.toBeInTheDocument();
  });
});
