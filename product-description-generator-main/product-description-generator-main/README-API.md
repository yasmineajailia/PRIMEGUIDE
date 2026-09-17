# Product Description Generator API

This is a REST API for the Product Description Generator application, built with FastAPI and Python. It provides endpoints for generating product descriptions, marketing recommendations, trend predictions, and audio generation.

## Prerequisites

- Python 3.9+
- Docker (optional, for containerization)
- Node.js 16+ (for the React frontend example)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd product-description-generator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn python-multipart
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   # Google API Key for Gemini
   GOOGLE_API_KEY=your_google_api_key
   
   # ElevenLabs API Key for text-to-speech
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

## Running the API

### Development Mode

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t product-description-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env product-description-api
   ```

## API Endpoints

### 1. Predict Product Trend

**Endpoint:** `POST /predict-trend`

Predicts market trends for a product based on various factors.

**Request Body:**
```json
{
  "product_name": "string",
  "category": "string",
  "initial_price": 0,
  "marketing_budget": 0,
  "time_period": 30,
  "seasonality_factor": 1.0,
  "competition_level": 0.5
}
```

### 2. Get Marketing Recommendations

**Endpoint:** `POST /get-marketing-recommendations`

Provides marketing strategy recommendations based on business parameters.

**Request Body:**
```json
{
  "industry": "string",
  "budget_amount": 0,
  "daily_hours": 0,
  "technical_skill": 0,
  "audience_size": "string",
  "goal": "string"
}
```

### 3. Generate Audio

**Endpoint:** `POST /generate-audio`

Converts text to speech using the ElevenLabs API.

**Request Body:**
```json
{
  "text": "This is the text to convert to speech",
  "voice_id": "Aria",
  "style": 0.5
}
```

### 4. Available Voices

**Endpoint:** `GET /available-voices`

Returns a list of available voices for audio generation.

### 5. Generate Product Image

**Endpoint:** `POST /generate-product-image`

Generates a product image based on provided details.

**Request Body:**
```json
{
  "product_name": "Smart Home Security Camera",
  "keywords": "wireless, sleek design, modern",
  "image_style": "product",
  "image_size": "512x512"
}
```

## React Frontend Example

A sample React application is provided in the `react-example` directory. To run it:

1. Navigate to the `react-example` directory:
   ```bash
   cd react-example
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The React app will be available at `http://localhost:3000`

## Deployment

### Option 1: Docker

Build and push the Docker image to a container registry:

```bash
docker build -t yourusername/product-description-api .
docker push yourusername/product-description-api
```

Then deploy to any container orchestration platform (Kubernetes, ECS, etc.).

### Option 2: Serverless

You can deploy the API as a serverless function using:
- AWS Lambda with API Gateway
- Google Cloud Functions
- Azure Functions

### Option 3: VPS

1. Clone the repository on your VPS
2. Set up a reverse proxy (Nginx, Apache)
3. Use a process manager like PM2 or Gunicorn with Uvicorn workers

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | API key for Google's Generative AI | Yes | - |
| `ELEVENLABS_API_KEY` | API key for ElevenLabs text-to-speech | No | - |
| `PORT` | Port to run the API on | No | 8000 |
| `ENVIRONMENT` | Environment (development/production) | No | development |

## Troubleshooting

- If you encounter CUDA out of memory errors, try reducing the batch size or using a smaller model.
- Ensure all required environment variables are set.
- Check the logs for detailed error messages.

## License

[Your License Here]
