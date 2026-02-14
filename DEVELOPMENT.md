# Development Guide

## Technical Features Added

### 1. Performance Monitoring
- **System Stats**: CPU, Memory, Disk usage monitoring
- **Cache Management**: In-memory caching with TTL support
- **Performance Endpoints**: `/api/v1/performance/stats` and `/api/v1/performance/cache/clear`

### 2. Rate Limiting
- **Protection**: 100 requests per minute per IP
- **Configurable**: Adjustable rate limits
- **Graceful Handling**: Proper HTTP 429 responses

### 3. Enhanced Text Analysis
- **Better Calibration**: Improved real news vs misinformation detection
- **Keyword Balance**: More nuanced keyword analysis
- **Confidence Adjustment**: Dynamic confidence based on content

### 4. API Improvements
- **Multi-source Support**: Social media and news article analysis
- **Error Handling**: Comprehensive error catching and logging
- **Documentation**: Auto-generated OpenAPI docs

## Setup Instructions

### Backend
```bash
cd MitraVerify-Backend
pip install -r requirements.txt
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd mitraverify-frontend
npm install
npm run dev
```

## Environment Variables
Create `.env` file in backend:
```
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

## API Endpoints

### Core Verification
- `POST /api/v1/verify` - General content verification
- `POST /api/v1/verify/text` - Text-only verification
- `POST /api/v1/verify/image` - Image-only verification

### Multi-Source Analysis
- `POST /api/v1/multi-source/analyze-social-post` - Social media analysis
- `POST /api/v1/multi-source/analyze-news-article` - News article analysis
- `POST /api/v1/multi-source/batch-analyze-urls` - Batch URL analysis

### Monitoring
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/performance/stats` - Performance statistics
- `POST /api/v1/performance/cache/clear` - Clear cache

## Testing
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Health**: http://localhost:8000/api/v1/health
