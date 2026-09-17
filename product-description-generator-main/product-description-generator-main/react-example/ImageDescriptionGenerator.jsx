import { useState } from 'react';

function ImageDescriptionGenerator() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // API URL - change this to match your API location
  const API_URL = 'http://localhost:8000';

  // Handle image selection
  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      
      // Create preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Generate description from image
  const generateDescription = async (e) => {
    e.preventDefault();
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);
    setDescription('');

    try {
      // Create a FormData object to send the file
      const formData = new FormData();
      formData.append('image', selectedImage);

      const response = await fetch(`${API_URL}/generate-description-from-image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to generate description: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        setDescription(data.description);
      } else {
        throw new Error(data.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('Error generating description from image:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Image-to-Text Product Description Generator</h2>
      
      <form onSubmit={generateDescription} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Upload Product Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="mt-1 block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
          <p className="mt-1 text-xs text-gray-500">Upload a clear image of the product</p>
        </div>

        {imagePreview && (
          <div className="mt-2 flex justify-center">
            <img 
              src={imagePreview} 
              alt="Product preview" 
              className="h-48 object-contain rounded-md" 
            />
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !selectedImage}
          className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {loading ? 'Generating...' : 'Generate Description from Image'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
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
  );
}

export default ImageDescriptionGenerator;
