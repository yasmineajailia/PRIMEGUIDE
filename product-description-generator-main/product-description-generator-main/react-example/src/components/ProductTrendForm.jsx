import React, { useState } from 'react';
import TrendChart from './TrendChart';
import SocialMediaCalendar from './SocialMediaCalendar';
import { exampleProducts } from '../data/exampleProducts';

const ProductTrendForm = () => {
  // Predefined categories and demographics
  const categories = [
    "Clothing", "Electronics", "Home Decor", "Beauty", "Health", 
    "Fitness", "Kitchen", "Office", "Outdoors", "Pet Supplies",
    "Food & Beverage", "Toys", "Books", "Art Supplies", "Handmade"
  ];

  const demographics = [
    "Young Adults", "Professionals", "Parents", "Seniors", "Teenagers",
    "Children", "Men", "Women", "Families", "Students"
  ];

  const [formData, setFormData] = useState({
    product_name: '',
    category: 'Electronics',
    target_demographic: 'Young Adults',
    initial_price: '',
    marketing_budget: '',
    time_period: '30',
    seasonality_factor: '1.0',
    competition_level: '0.5',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showExamples, setShowExamples] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // If category changes, hide examples panel
    if (name === 'category') {
      setShowExamples(false);
    }
  };

  const handleExampleSelect = (example) => {
    setFormData(prev => ({
      ...prev,
      product_name: example.name,
      initial_price: example.price.toString(),
      marketing_budget: example.marketing_budget.toString(),
      target_demographic: example.target_demographic,
      seasonality_factor: example.seasonality_factor.toString(),
      competition_level: example.competition_level.toString()
    }));
    setShowExamples(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/predict-trend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          initial_price: parseFloat(formData.initial_price),
          marketing_budget: parseFloat(formData.marketing_budget),
          time_period: parseInt(formData.time_period, 10),
          seasonality_factor: parseFloat(formData.seasonality_factor),
          competition_level: parseFloat(formData.competition_level),
          target_demographic: formData.target_demographic,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch prediction');
      }

      const data = await response.json();
      setResult(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Product Trend Prediction</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
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
            <label className="block text-sm font-medium text-gray-700">
              Category
              <button
                type="button"
                onClick={() => setShowExamples(!showExamples)}
                className="ml-2 text-xs text-indigo-600 hover:text-indigo-800"
              >
                {showExamples ? 'Hide Examples' : 'Show Examples'}
              </button>
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Example Products Panel */}
          {showExamples && (
            <div className="md:col-span-2 bg-gray-50 p-4 rounded-lg">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Example Products for {formData.category}</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {exampleProducts[formData.category]?.map((example, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleExampleSelect(example)}
                    className="text-left p-3 bg-white rounded-md shadow-sm hover:shadow-md transition-shadow border border-gray-200"
                  >
                    <div className="font-medium text-gray-900">{example.name}</div>
                    <div className="text-sm text-gray-500">
                      Price: ${example.price} • Marketing: ${example.marketing_budget}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">Target Demographic</label>
            <select
              name="target_demographic"
              value={formData.target_demographic}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            >
              {demographics.map(demo => (
                <option key={demo} value={demo}>{demo}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Initial Price ($)</label>
            <input
              type="number"
              step="0.01"
              name="initial_price"
              value={formData.initial_price}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Marketing Budget ($)</label>
            <input
              type="number"
              step="0.01"
              name="marketing_budget"
              value={formData.marketing_budget}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Time Period (days)</label>
            <input
              type="number"
              name="time_period"
              value={formData.time_period}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Seasonality Factor (1.0-3.0)</label>
            <input
              type="number"
              step="0.1"
              min="1.0"
              max="3.0"
              name="seasonality_factor"
              value={formData.seasonality_factor}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Competition Level (0.1-1.0)</label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              max="1.0"
              name="competition_level"
              value={formData.competition_level}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
        </div>
        
        <div className="mt-6">
          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Predicting...' : 'Predict Trend'}
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
          <h3 className="text-lg font-medium text-gray-900">Prediction Results</h3>
          
          {/* Chart Visualization */}
          <div className="mt-4">
            <TrendChart data={result} />
          </div>
          
          {/* Social Media Calendar */}
          <SocialMediaCalendar 
            data={result} 
            productName={formData.product_name}
            category={formData.category}
            demographic={formData.target_demographic}
          />
          
          {/* Raw Data (for debugging) */}
          <div className="mt-4">
            <details className="text-sm">
              <summary className="text-gray-700 cursor-pointer hover:text-indigo-600">View Raw Data</summary>
              <pre className="mt-2 p-4 bg-white rounded overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductTrendForm;
