# 🚀 Content Generation Platform

A full-stack AI-powered content generation platform built for **Small and Medium Enterprises (SMEs)**. It combines a Python/FastAPI AI backend with a React + Node.js frontend to deliver intelligent product descriptions, marketing strategy recommendations, product trend predictions, AI-generated images, animated GIFs, and text-to-speech audio all in one place.

---

## 📁 Project Structure

```
Content-Generation/
├── product-description-generator-main/   # 🐍 Python / FastAPI AI Backend
│   └── product-description-generator-main/
│       ├── api.py                        # Core FastAPI app (text, image, gif, trend endpoints)
│       ├── fastapi_app.py                # Extended FastAPI app (Gemini AI, audio, uploads)
│       ├── app.py                        # Standalone app entry point
│       ├── generators/                   # AI generation modules
│       │   ├── text_generator.py         # T5 / Flan-T5 / custom text generation
│       │   ├── image_generator.py        # Stable Diffusion image generation
│       │   ├── gif_generator.py          # Animated GIF generation
│       │   └── audio_generator.py        # ElevenLabs text-to-speech
│       ├── models/                       # Trained ML models
│       ├── trainers/                     # Model training scripts
│       ├── utils/                        # Shared utilities (logging, helpers)
│       ├── data/                         # Strategy & trend datasets (CSV)
│       ├── static/                       # Served static assets
│       ├── requirements.txt              # Python dependencies
│       ├── Dockerfile                    # Docker support
│       └── README.md                     # Backend-specific docs
│
├── react-node-App-master/                # ⚛️ React + Node.js Frontend
│   ├── src/
│   │   ├── main.jsx                      # React app entry point
│   │   ├── components/
│   │   │   ├── List.jsx                  # Ingredient list display
│   │   │   ├── ListItem.jsx              # Individual list item
│   │   │   └── ListManager.jsx           # Full CRUD list manager
│   │   └── services/                     # API service layer
│   ├── public/                           # Static HTML + built JS
│   ├── server.js                         # Express.js backend (port 6060)
│   ├── package.json                      # Node.js dependencies
│   └── README.md                         # Frontend-specific docs
│
└── README.md                             # ← You are here
```

---

## ✨ Features

### 🤖 AI Backend (Python / FastAPI)
| Feature | Description |
|---|---|
| **Product Description Generation** | Generate compelling product descriptions using T5, Flan-T5, or Google Gemini |
| **Product Image Generation** | Create AI-generated product images via Stable Diffusion |
| **Animated GIF Generation** | Generate animated GIFs from product descriptions |
| **Text-to-Speech Audio** | Convert marketing copy to realistic audio with ElevenLabs |
| **Marketing Strategy Recommender** | Get personalised digital marketing strategies based on your SME profile |
| **Product Trend Prediction** | Forecast sales trends with ROI estimates using ML models |
| **Multiple UI Interfaces** | CLI, Tkinter GUI, Accessible GUI, Streamlit web UI |

### ⚛️ Frontend (React + Node.js)
| Feature | Description |
|---|---|
| **React SPA** | Component-based single-page application |
| **Express API** | Lightweight REST API server for data management |
| **Live Data** | Real-time fetch & display of ingredient/product lists |
| **CRUD Operations** | Add and view items via POST/GET endpoints |

---

## 🛠️ Tech Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: FastAPI + Uvicorn
- **AI/ML**: HuggingFace Transformers, Stable Diffusion (diffusers), Sentence Transformers, scikit-learn, FAISS
- **LLM**: Google Gemini (via `google-generativeai`)
- **TTS**: ElevenLabs
- **Data**: Pandas, NumPy
- **Containerisation**: Docker

### Frontend
- **UI**: React 15 + Babel + Browserify
- **Server**: Node.js + Express.js
- **HTTP**: Fetch API (whatwg-fetch polyfill)

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 14+ with npm
- Git

---

### 1. Clone the Repository

```bash
git clone https://github.com/yasmineajailia/Content-Generation.git
cd Content-Generation
```

---

### 2. Set Up the Python Backend

```bash
cd product-description-generator-main/product-description-generator-main

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the backend directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

> **🔑 Get API Keys:**
> - Google Gemini: https://makersuite.google.com/app/apikey
> - ElevenLabs: https://elevenlabs.io/

#### Run the API Server

```bash
# Option 1: FastAPI with Gemini AI (recommended)
uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000

# Option 2: Lightweight API (no Gemini required)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Option 3: Use the batch script (Windows)
run_api.bat
```

The API will be live at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

### 3. Set Up the React + Node.js Frontend

```bash
cd react-node-App-master

# Install dependencies
npm install

# Build the React app
npm run build

# Start the Express server (port 6060)
node server.js
```

Then open **http://localhost:8080** in your browser.

---

### 4. Docker (Backend only)

```bash
cd product-description-generator-main/product-description-generator-main
docker build -t content-gen-api .
docker run -p 8000:8000 --env-file .env content-gen-api
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/generate-product-description` | Generate product text description |
| `POST` | `/generate-product-image` | Generate product image |
| `POST` | `/generate-product-gif` | Generate animated GIF |
| `POST` | `/predict-trend` | Predict product sales trend & ROI |
| `POST` | `/get-marketing-recommendations` | Get personalised marketing strategies |

Full interactive API documentation is available at `/docs` when the server is running.

---

## 🖥️ Additional Interfaces

### Streamlit Web App
```bash
streamlit run simple_web.py
```

### Tkinter GUI
```bash
python gui_recommender.py        # Standard GUI
python accessible_futuristic_gui.py  # Enhanced accessible GUI
```

### Command-Line Interface
```bash
python marketing_recommender_cli.py
```

---

## 📊 How the Recommendation Engine Works

The marketing strategy recommender uses **content-based filtering with cosine similarity**:

1. **Profile Creation**  Your inputs (industry, budget, hours, goals) form a numerical vector
2. **Strategy Dataset**  A curated CSV of digital marketing strategies with attributes
3. **Similarity Scoring**  Cosine similarity between your profile and each strategy
4. **Ranked Results**  Top-5 strategies filtered by industry & ranked by expected ROI

---

## 🔒 Security Notes

- **Never commit your `.env` file**  it is included in `.gitignore`
- Rotate your API keys immediately if they are ever exposed
- The CORS policy in development allows all origins  restrict this in production

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **ISC License**  see the [LICENSE](LICENSE) file for details.

---

## 👩‍💻 Author

**Yasmine Ajailia**  
📧 yasmine.laajailia@esprit.tn  
🔗 [GitHub](https://github.com/yasmineajailia)

---

*Built with ❤️ for SMEs looking to supercharge their digital marketing with AI.*
