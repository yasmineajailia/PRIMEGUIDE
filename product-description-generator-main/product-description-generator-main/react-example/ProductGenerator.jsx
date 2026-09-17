import { useState } from 'react';

function ProductGenerator() {
  // State for product description form
  const [descForm, setDescForm] = useState({
    productName: '',
    keywords: '',
    tone: 'Professional',
    modelType: 'default'
  });
  const [description, setDescription] = useState('');
  const [descLoading, setDescLoading] = useState(false);
  const [descError, setDescError] = useState(null);

  // State for product image form
  const [imgForm, setImgForm] = useState({
    productName: '',
    keywords: '',
    imageStyle: 'product',
    imageSize: '512x512'
  });
  const [imageUrl, setImageUrl] = useState('');
  const [imgLoading, setImgLoading] = useState(false);
  const [imgError, setImgError] = useState(null);

  // State for GIF form
  const [gifForm, setGifForm] = useState({
    description: '',
    numFrames: 6,
    style: 'product',
    imageSize: '512x512'
  });
  const [gifUrl, setGifUrl] = useState('');
  const [gifLoading, setGifLoading] = useState(false);
  const [gifError, setGifError] = useState(null);

  // API URL - change this to match your API location
  const API_URL = 'http://localhost:8000';

  // Handle description form changes
  const handleDescChange = (e) => {
    const { name, value } = e.target;
    setDescForm((prev) => ({ ...prev, [name]: value }));
  };

  // Handle image form changes
  const handleImgChange = (e) => {
    const { name, value } = e.target;
    setImgForm((prev) => ({ ...prev, [name]: value }));
  };

  // Handle GIF form changes
  const handleGifChange = (e) => {
    const { name, value } = e.target;
    setGifForm((prev) => ({ ...prev, [name]: name === 'numFrames' ? parseInt(value) : value }));
  };

  // Generate product description
  const generateDescription = async (e) => {
    e.preventDefault();
    setDescLoading(true);
    setDescError(null);

    try {
      const response = await fetch(`${API_URL}/generate-product-description`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: descForm.productName,
          keywords: descForm.keywords,
          tone: descForm.tone,
          model_type: descForm.modelType
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate description');
      }

      const data = await response.json();
      setDescription(data.description);
    } catch (error) {
      console.error('Error generating description:', error);
      setDescError(error.message);
    } finally {
      setDescLoading(false);
    }
  };

  // Generate product image
  const generateImage = async (e) => {
    e.preventDefault();
    setImgLoading(true);
    setImgError(null);

    try {
      const response = await fetch(`${API_URL}/generate-product-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: imgForm.productName,
          keywords: imgForm.keywords,
          image_style: imgForm.imageStyle,
          image_size: imgForm.imageSize
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate image');
      }

      const data = await response.json();
      if (data.success) {
        setImageUrl(`${API_URL}${data.image_url}`);
      } else {
        throw new Error(data.status || 'Unknown error');
      }
    } catch (error) {
      console.error('Error generating image:', error);
      setImgError(error.message);
    } finally {
      setImgLoading(false);
    }
  };

  // Generate product GIF
  const generateGif = async (e) => {
    e.preventDefault();
    setGifLoading(true);
    setGifError(null);

    try {
      const response = await fetch(`${API_URL}/generate-product-gif`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description_text: gifForm.description,
          num_frames: gifForm.numFrames,
          image_size: gifForm.imageSize,
          style: gifForm.style
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate GIF');
      }

      const data = await response.json();
      if (data.success) {
        setGifUrl(`${API_URL}${data.gif_url}`);
      } else {
        throw new Error(data.status || 'Unknown error');
      }
    } catch (error) {
      console.error('Error generating GIF:', error);
      setGifError(error.message);
    } finally {
      setGifLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">AI Product Generator</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Product Description Generator */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Product Description Generator</h2>
          <form onSubmit={generateDescription} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Product Name</label>
              <input
                type="text"
                name="productName"
                value={descForm.productName}
                onChange={handleDescChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Keywords (Optional)</label>
              <input
                type="text"
                name="keywords"
                value={descForm.keywords}
                onChange={handleDescChange}
                placeholder="Enter keywords separated by commas"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Tone</label>
              <select
                name="tone"
                value={descForm.tone}
                onChange={handleDescChange}
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
              <label className="block text-sm font-medium text-gray-700">Model</label>
              <select
                name="modelType"
                value={descForm.modelType}
                onChange={handleDescChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="default">Default</option>
                <option value="t5">T5 Model</option>
                <option value="flan-t5">FLAN-T5 Model</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={descLoading}
              className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {descLoading ? 'Generating...' : 'Generate Description'}
            </button>
          </form>

          {descError && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
              {descError}
            </div>
          )}

          {description && (
            <div className="mt-6">
              <h3 className="font-medium text-lg">Generated Description:</h3>
              <div className="mt-2 p-4 bg-gray-50 rounded-md whitespace-pre-wrap">
                {description}
              </div>
            </div>
          )}
        </div>

        {/* Product Image Generator */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Product Image Generator</h2>
          <form onSubmit={generateImage} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Product Name</label>
              <input
                type="text"
                name="productName"
                value={imgForm.productName}
                onChange={handleImgChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Keywords (Optional)</label>
              <input
                type="text"
                name="keywords"
                value={imgForm.keywords}
                onChange={handleImgChange}
                placeholder="Enter keywords separated by commas"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Image Style</label>
              <select
                name="imageStyle"
                value={imgForm.imageStyle}
                onChange={handleImgChange}
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
                name="imageSize"
                value={imgForm.imageSize}
                onChange={handleImgChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="512x512">512x512</option>
                <option value="768x512">768x512</option>
                <option value="512x768">512x768</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={imgLoading}
              className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {imgLoading ? 'Generating...' : 'Generate Image'}
            </button>
          </form>

          {imgError && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
              {imgError}
            </div>
          )}

          {imageUrl && (
            <div className="mt-6">
              <h3 className="font-medium text-lg">Generated Image:</h3>
              <div className="mt-2 flex justify-center">
                <img 
                  src={imageUrl} 
                  alt="Generated product" 
                  className="max-w-full h-auto rounded-md shadow-sm" 
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Product GIF Generator */}
      <div className="bg-white p-6 rounded-lg shadow-lg mt-8">
        <h2 className="text-xl font-semibold mb-4">Product GIF Generator</h2>
        <form onSubmit={generateGif} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Product Description</label>
            <textarea
              name="description"
              value={gifForm.description}
              onChange={handleGifChange}
              rows="3"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="Enter a detailed description of the product for animation"
              required
            ></textarea>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Frames</label>
              <input
                type="number"
                name="numFrames"
                value={gifForm.numFrames}
                onChange={handleGifChange}
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
                value={gifForm.style}
                onChange={handleGifChange}
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
                name="imageSize"
                value={gifForm.imageSize}
                onChange={handleGifChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="512x512">512x512</option>
                <option value="384x384">384x384 (Faster)</option>
                <option value="256x256">256x256 (Fastest)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={gifLoading}
            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            {gifLoading ? 'Generating... (This may take a while)' : 'Generate GIF'}
          </button>
        </form>

        {gifError && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
            {gifError}
          </div>
        )}

        {gifUrl && (
          <div className="mt-6">
            <h3 className="font-medium text-lg">Generated GIF:</h3>
            <div className="mt-2 flex justify-center">
              <img 
                src={gifUrl} 
                alt="Generated product animation" 
                className="max-w-full h-auto rounded-md shadow-sm" 
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductGenerator;
