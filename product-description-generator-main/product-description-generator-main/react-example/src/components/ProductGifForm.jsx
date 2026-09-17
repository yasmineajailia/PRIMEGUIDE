import React, { useState } from 'react';

const ProductGifForm = () => {
  const [formData, setFormData] = useState({
    description_text: '',
    num_frames: 6,
    image_size: '512x512',
    style: 'product'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'num_frames' ? parseInt(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/generate-product-gif', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to generate GIF');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Product GIF Generator</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Product Description</label>
            <textarea
              name="description_text"
              value={formData.description_text}
              onChange={handleChange}
              rows={4}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
              placeholder="Enter a detailed description of the product for animation"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Number of Frames</label>
            <input
              type="number"
              name="num_frames"
              value={formData.num_frames}
              onChange={handleChange}
              min="3"
              max="12"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            <p className="mt-1 text-xs text-gray-500">More frames = longer generation time (3-12 recommended)</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">GIF Style</label>
            <select
              name="style"
              value={formData.style}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="product">Product Photography</option>
              <option value="realistic">Realistic</option>
              <option value="artistic">Artistic</option>
              <option value="minimalist">Minimalist</option>
              <option value="isometric">Isometric</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Image Size</label>
            <select
              name="image_size"
              value={formData.image_size}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="512x512">512x512</option>
              <option value="384x384">384x384 (Faster)</option>
              <option value="256x256">256x256 (Fastest)</option>
            </select>
          </div>
        </div>
        
        <div className="mt-6">
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating... (This may take a while)' : 'Generate GIF'}
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
          <h3 className="text-lg font-medium text-gray-900">Generated GIF</h3>
          <div className="mt-2 p-4 bg-white rounded border border-gray-200 flex justify-center">
            <img 
              src={`http://localhost:8000${result.gif_url}`} 
              alt="Generated GIF" 
              className="rounded max-w-full h-auto"
            />
          </div>
          <p className="mt-2 text-sm text-gray-500">{result.status}</p>
        </div>
      )}

      {result && !result.success && (
        <div className="mt-4 p-4 text-sm text-red-700 bg-red-100 rounded-lg">
          {result.status}
        </div>
      )}
    </div>
  );
};

export default ProductGifForm;
