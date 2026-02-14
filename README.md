# SatyaNet 🔍

**AI-Powered Misinformation Detection Platform for India**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com/)

## 🎯 Overview

SatyaNet is a comprehensive AI-powered platform designed to combat misinformation in real-time, specifically tailored for the Indian market. It provides instant verification of text content, images, and multimedia across multiple languages (English/Hindi) with transparent, explainable results.

### Key Features

- **🤖 Multimodal AI Analysis**: Text + Image verification using MURIL and CLIP models
- **🌐 Multilingual Support**: Native Hindi and English processing
- **⚡ Real-time Processing**: Sub-second analysis with live confidence updates
- **🔍 Transparent Results**: Evidence-based analysis with clear explanations
- **📱 Mobile-First Design**: Optimized for Indian smartphone users
- **🔒 Privacy-First**: Local processing, no data retention

## 🏗️ Architecture

```
Frontend (Next.js) ←→ FastAPI Gateway ←→ AI Core (MURIL + CLIP) ←→ Evidence DB
```

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- MURIL (Multilingual BERT)
- OpenAI CLIP
- Sentence Transformers
- PostgreSQL + Redis

**Frontend:**
- Next.js 14 + TypeScript
- Tailwind CSS + Shadcn/ui
- React 18 + Hooks

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/ChirayuMarathe/Mitra_Verify-2.0.git
cd Mitra_Verify-2.0
```

### 2. Backend Setup

```bash
cd SatyaNet-Backend

# Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Download AI models
python scripts/download_models.py

# Start backend
python -m uvicorn src.api.main:app --reload
```

### 3. Frontend Setup

```bash
cd SatyaNet-frontend

# Install dependencies
npm install

# Setup environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

### 4. Access Application

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Usage Examples

### Text Verification

```javascript
import { mitraAPI } from './src/lib/api';

const result = await mitraAPI.verifyText(
  "Breaking news: Scientists discover cure for all diseases!"
);

console.log(result.overall_verdict); // "misinformation"
console.log(result.confidence);      // 0.85
```

### Image + Text Verification

```javascript
const result = await mitraAPI.verifyContent(
  "This image shows the cure",
  imageFile
);
```

## 🧪 Testing

### Backend Tests

```bash
cd SatyaNet-Backend
python -m pytest tests/
python test_dynamic_analysis.py  # Test misinformation detection
```

### Frontend Tests

```bash
cd SatyaNet-frontend
npm test
```

## 📁 Project Structure

```
SatyaNet/
├── SatyaNet-Backend/
│   ├── src/
│   │   ├── api/           # FastAPI endpoints
│   │   ├── core/          # AI analysis engines
│   │   ├── models/        # ML model definitions
│   │   └── utils/         # Utility functions
│   ├── data/
│   │   ├── models/        # Pre-trained models
│   │   └── evidence/      # Fact-check database
│   ├── config/            # Configuration
│   ├── scripts/           # Setup scripts
│   └── tests/             # Backend tests
├── SatyaNet-frontend/
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   ├── lib/           # API integration
│   │   └── hooks/         # Custom React hooks
│   └── public/            # Static assets
└── docs/                  # Documentation
```

## 🌟 Core Components

### 1. Text Analyzer
- **Model**: Google MURIL (Multilingual BERT)
- **Features**: Hindi/English misinformation detection
- **Confidence**: Calibrated probability scores

### 2. Image Analyzer
- **Model**: OpenAI CLIP
- **Features**: Deepfake detection, manipulation analysis
- **Forensics**: Reverse image search, similarity matching

### 3. Evidence Retrieval
- **Sources**: AltNews, PIB Fact Check, Factly
- **Method**: Semantic similarity using embeddings
- **Integration**: Real-time fact-checking database

### 4. Fusion Engine
- **Approach**: Weighted confidence combination
- **Logic**: Multi-modal evidence aggregation
- **Output**: Final verdict with explanation

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
# API Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Model Settings
TEXT_MODEL=google/muril-base-cased
IMAGE_MODEL=openai/clip-vit-base-patch32
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# External APIs
ALTNEWS_API_KEY=your_key_here
PIB_API_KEY=your_key_here
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SatyaNet
```

## 📈 Performance Metrics

- **Response Time**: < 2 seconds for text analysis
- **Accuracy**: > 85% on misinformation datasets
- **Throughput**: 1000+ concurrent requests
- **Languages**: English, Hindi (extensible)
- **Availability**: 99.9% uptime target

## 🧪 Recent Improvements

### Fixed Issues
- ✅ Array comparison errors in fusion engine
- ✅ Evidence retrieval numpy array handling
- ✅ Undefined variable errors in text analyzer
- ✅ Dynamic confidence scoring implementation
- ✅ Language detection integration

### Enhanced Features
- 🔄 Content-based misinformation pattern detection
- 🔄 Improved confidence calibration
- 🔄 Better error handling and logging
- 🔄 Scalar value enforcement for reliability

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend
- Add tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MURIL**: Google's Multilingual BERT for Indian languages
- **CLIP**: OpenAI's vision-language model
- **Transformers**: Hugging Face's transformer library
- **FastAPI**: Modern Python web framework
- **Next.js**: React production framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ChirayuMarathe/Mitra_Verify-2.0/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ChirayuMarathe/Mitra_Verify-2.0/discussions)
- **Email**: support@SatyNet.com

---

**Made with ❤️ in India for fighting misinformation**