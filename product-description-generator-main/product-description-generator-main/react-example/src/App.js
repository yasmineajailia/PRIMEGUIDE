import React, { useState } from 'react';
import ProductTrendForm from './components/ProductTrendForm';
import AudioGenerator from './components/AudioGenerator';

function App() {
  const [activeTab, setActiveTab] = useState('trend');

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Product AI Hub
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
            AI-powered tools for product management and marketing
          </p>
        </div>
        
        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8 justify-center">
            <button
              onClick={() => setActiveTab('trend')}
              className={`pb-4 px-1 ${
                activeTab === 'trend'
                  ? 'border-indigo-500 text-indigo-600 border-b-2 font-medium'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Trend Prediction
            </button>
            <button
              onClick={() => setActiveTab('audio')}
              className={`pb-4 px-1 ${
                activeTab === 'audio'
                  ? 'border-indigo-500 text-indigo-600 border-b-2 font-medium'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Audio Generator
            </button>
          </nav>
        </div>
        
        <div className="mt-10">
          {activeTab === 'trend' && <ProductTrendForm />}
          {activeTab === 'audio' && <AudioGenerator />}
        </div>
      </div>
    </div>
  );
}

export default App;
