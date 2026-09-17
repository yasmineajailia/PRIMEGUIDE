# Product AI Hub - Integrated Application

This application combines AI-powered tools for product management and marketing, including trend prediction, text generation, image generation, and text-to-speech conversion.

## Features

- **Product Trend Prediction**: Predict market trends for your products
- **Text Generation**: Generate compelling product descriptions
- **Image Generation**: Create product images using AI
- **Audio Generation**: Convert text to speech with different voices

## Getting Started

### Prerequisites

- Python 3.9+ with pip
- Node.js 16+ with npm
- ElevenLabs API Key (for audio generation)
- Google API Key (for text generation)

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/product-description-generator.git
cd product-description-generator
```

2. Install Python dependencies:
```
pip install -r requirements.txt
```

3. Install React dependencies:
```
cd react-example
npm install
cd ..
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
GOOGLE_API_KEY=your_google_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### Running the Application

#### Backend (FastAPI)

Run the FastAPI server:

**Windows:**
```
run_api.bat
```

**Linux/Mac:**
```
chmod +x run_api.sh
./run_api.sh
```

The API will be available at http://localhost:8000

#### Frontend (React)

In a new terminal, start the React development server:

```
cd react-example
npm start
```

The React app will be available at http://localhost:3000

## Testing

### API Testing

To test all API endpoints:

**Windows:**
```
test_api.bat
```

**Linux/Mac:**
```
chmod +x test_api.sh
./test_api.sh
```

### Integration Testing

To run both backend and frontend tests:

**Windows:**
```
run_integration_tests.bat
```

**Linux/Mac:**
```
chmod +x run_integration_tests.sh
./run_integration_tests.sh
```

For more detailed testing instructions, see [INTEGRATION-TEST-GUIDE.md](INTEGRATION-TEST-GUIDE.md).

## API Documentation

- **FastAPI Documentation**: http://localhost:8000/docs
- API usage guide: [README-API.md](README-API.md)
- React integration guide: [README-API-INTEGRATION.md](react-example/README-API-INTEGRATION.md)

## Architecture

The application consists of:

1. **FastAPI Backend**: Handles API requests and integrates with AI services
2. **React Frontend**: User interface for interacting with the API
3. **AI Generators**: Modules for generating text, images, and audio
4. **Trend Prediction**: Algorithms for predicting product market trends

## Available React Components

- **ProductTrendForm**: Form for predicting product trends
- **AudioGenerator**: Component for text-to-speech conversion
- **ImageDescriptionGenerator**: Component for generating product images and descriptions

## Contributing

Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
