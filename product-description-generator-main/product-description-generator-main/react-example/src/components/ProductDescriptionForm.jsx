import React, { useState } from 'react';

const ProductDescriptionForm = () => {
  const [formData, setFormData] = useState({
    product_name: '',
    keywords: '',
    tone: 'Professional',
    model_type: 'default'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/generate-product-description', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to generate description');
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
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Product Description Generator</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Product Name</label>
            <input
              type="text"
              name="product_name"
              value={formData.product_name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Keywords (Optional)</label>
            <input
              type="text"
              name="keywords"
              value={formData.keywords}
              onChange={handleChange}
              placeholder="Enter keywords separated by commas"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Tone</label>
            <select
              name="tone"
              value={formData.tone}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="Professional">Professional</option>
              <option value="Casual">Casual</option>
              <option value="Enthusiastic">Enthusiastic</option>
              <option value="Formal">Formal</option>
              <option value="Friendly">Friendly</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Model Type</label>
            <select
              name="model_type"
              value={formData.model_type}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="default">Default</option>
              <option value="t5">T5 Model</option>
              <option value="flan-t5">FLAN-T5 Model</option>
            </select>
          </div>
        </div>
        
        <div className="mt-6">
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Generate Description'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="mt-4 p-4 text-sm text-red-700 bg-red-100 rounded-lg">
          Error: {error}
        </div>
      )}
      
      {result && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900">Generated Description</h3>
          <div className="mt-2 p-4 bg-white rounded border border-gray-200">
            {result.description && result.description.split('\n').map((paragraph, idx) => (
              <p key={idx} className={idx > 0 ? "mt-3" : ""}>
                {paragraph}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDescriptionForm;
