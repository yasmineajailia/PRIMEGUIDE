import React, { useState, useEffect } from 'react';
import { generateAudio, getAvailableVoices } from '../services/api';

const AudioGenerator = () => {
  const [formData, setFormData] = useState({
    text: '',
    voice_id: 'Aria',
    style: 0.5
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [voices, setVoices] = useState({});

  // Fetch available voices on component mount
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const availableVoices = await getAvailableVoices();
        setVoices(availableVoices);
      } catch (err) {
        console.error('Failed to fetch voices:', err);
        setError('Failed to load available voices');
      }
    };

    fetchVoices();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'style' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const data = await generateAudio(formData);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate audio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Audio Generator</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Text to Convert</label>
            <textarea
              name="text"
              value={formData.text}
              onChange={handleChange}
              rows={4}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="Enter the text you want to convert to speech"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Voice</label>
            <select
              name="voice_id"
              value={formData.voice_id}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              {Object.entries(voices).map(([id, description]) => (
                <option key={id} value={id}>{id} - {description}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Style Intensity: {formData.style}
            </label>
            <input
              type="range"
              name="style"
              min="0"
              max="1"
              step="0.1"
              value={formData.style}
              onChange={handleChange}
              className="mt-1 block w-full"
            />
          </div>
        </div>
        
        <div className="mt-6">
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Generate Audio'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="mt-4 p-4 text-sm text-red-700 bg-red-100 rounded-lg">
          Error: {error}
        </div>
      )}
      
      {result && result.success && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900">Generated Audio</h3>
          <div className="mt-4 flex justify-center">
            <audio 
              controls
              src={`http://localhost:8000${result.audio_url}`}
              className="w-full"
            >
              Your browser does not support the audio element.
            </audio>
          </div>
          <div className="mt-4 flex justify-center">
            <a 
              href={`http://localhost:8000${result.audio_url}`}
              download
              className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Download Audio
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioGenerator;
