# AI MON - Smart API Monitoring & Auto Debug Tool

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/FastAPI-0.109.0-purple.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18.2-orange.svg" alt="React">
</p>

AI MON is a production-ready smart API monitoring and auto-debug tool that provides real-time API monitoring, anomaly detection, failure analysis, and AI-powered debugging insights.

## 🚀 Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **API Registration**: Add APIs with URL, HTTP method, monitoring interval, expected status code, and timeout threshold
- **Background Monitoring**: Async monitoring engine that periodically checks registered APIs
- **Real-time Dashboard**: Live dashboard with uptime percentage, response time graphs, and error rates
- **Anomaly Detection**: Statistical anomaly detection using rolling mean and standard deviation (Z-score method)
- **Repeated Failure Detection**: Tracks consecutive failures and triggers alerts
- **AI Integration**: Collects failure logs and sends them to LLM for analysis (with mock mode fallback)
- **Email Alerts**: Sends notifications when APIs fail consecutively (3+ failures)
- **WebSocket Support**: Real-time updates when health checks complete

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: SQLAlchemy async with SQLite/PostgreSQL support
- **Authentication**: JWT with python-jose
- **HTTP Client**: httpx for async monitoring
- **AI**: OpenAI SDK (with mock mode fallback)
- **Rate Limiting**: SlowAPI

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context + React Query
- **Charts**: Recharts
- **Routing**: React Router v6

## 📋 Architecture Overview

```
ai-mon/
├── backend/
│   ├── app/
│   │   ├── ai/                    # AI client and prompt templates
│   │   ├── api/                   # REST API endpoints
│   │   ├── core/                  # Config, database, security
│   │   ├── middleware/            # CSP, CORS middleware
│   │   ├── models/                # SQLAlchemy ORM models
│   │   ├── monitoring_engine/     # Health checker and scheduler
│   │   ├── schemas/                # Pydantic validation schemas
│   │   ├── services/               # Business logic
│   │   └── utils/                 # Utilities
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                   # API clients
│   │   ├── components/            # React components
│   │   ├── context/               # React context
│   │   ├── hooks/                 # Custom hooks
│   │   ├── pages/                 # Page components
│   │   ├── types/                 # TypeScript types
│   │   └── utils/                 # Utilities
│   ├── package.json
│   └── vite.config.ts
├── api/                           # Vercel serverless functions
├── vercel.json                    # Vercel configuration
└── README.md
```

## 🚦 Deployment Guide

### Option 1: Deploy on Render (Recommended for Beginners)

#### Why Render?
- ✅ Free tier available
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ Persistent disk for SQLite database

#### Step-by-Step:

1. **Connect Your Repository**
   - Go to [render.com](https://render.com) and sign up
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure the Service**
   | Field | Value |
   |-------|-------|
   | Name | `ai-mon-backend` |
   | Environment | `Python` |
   | Region | Choose closest to you |
   | Branch | `main` |
   | Build Command | `pip install -r backend/requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |

3. **Add Environment Variables**
   Click "Advanced" and add these:

   ```
   DEBUG=false
   ENVIRONMENT=production
   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
   DATABASE_URL=sqlite+aiosqlite:///./aimon.db
   CORS_ORIGINS=https://your-frontend.onrender.com
   OPENAI_API_KEY=<your-key-if-using-ai>
   ```

4. **Add Persistent Disk (Recommended)**
   - Click "Add Persistent Disk"
   - Name: `ai-mon-data`
   - Size: `1 GB` (free)
   - Mount Path: `/app/data`

   If using persistent disk, change DATABASE_URL to:
   ```
   sqlite+aiosqlite:///./data/aimon.db
   ```

5. **Deploy!** 🚀
   - Click "Create Web Service"
   - Wait for build to complete (~5-10 minutes)
   - Visit: `https://your-service.onrender.com/health/live`

---

### Option 2: Deploy on Vercel

> Already covered in detail below

### Prerequisites
- Node.js 18+
- Python 3.10+
- Vercel account

### Quick Deploy

1. **Fork or clone this repository**

2. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the `backend` directory (copy from `backend/.env.example`):
   ```bash
   # Required for production
   SECRET_KEY=your-secure-secret-key-here
   ENVIRONMENT=production
   DEBUG=false
   
   # Database (PostgreSQL recommended for production)
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   
   # Optional: AI Integration
   # OPENAI_API_KEY=sk-...
   
   # Optional: Email (for alerts)
   # SMTP_USER=your-email@gmail.com
   # SMTP_PASSWORD=your-app-password
   ```

4. **Deploy to Vercel**:
   ```bash
   vercel
   ```

   Or connect your GitHub repository to Vercel for automatic deployments.

5. **Configure Environment Variables in Vercel Dashboard**:
   - Go to your project settings
   - Add environment variables:
     - `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
     - `ENVIRONMENT` = `production`
     - `DEBUG` = `false`
     - `DATABASE_URL` = your PostgreSQL connection string
     - `CORS_ORIGINS` = `https://your-project.vercel.app`

### Local Development

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # And configure
   python -m uvicorn app.main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cp .env.example .env  # And configure
   npm run dev
   ```

## 📝 Environment Variables Setup

### Backend Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT secret key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`) | Yes | Auto-generated |
| `ENVIRONMENT` | Environment: `development` or `production` | No | `development` |
| `DEBUG` | Enable debug mode | No | `false` |
| `DATABASE_URL` | Database connection string | No | `sqlite+aiosqlite:///./aimon.db` |
| `ALGORITHM` | JWT algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | No | `7` |
| `OPENAI_API_KEY` | OpenAI API key for AI insights | No | - |
| `AI_MODEL` | AI model to use | No | `gpt-4` |
| `SMTP_HOST` | Email SMTP host | No | `smtp.gmail.com` |
| `SMTP_PORT` | Email SMTP port | No | `587` |
| `SMTP_USER` | Email username | No | - |
| `SMTP_PASSWORD` | Email password | No | - |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | No | Localhost |
| `MONITORING_INTERVAL_SECONDS` | Health check interval | No | `60` |
| `MAX_CONCURRENT_CHECKS` | Max concurrent health checks | No | `100` |

### Frontend Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API URL | Yes | `http://localhost:8000/api` |

## 🔒 Security Measures Implemented

### Authentication & Authorization
- JWT-based authentication with access and refresh tokens
- Token expiration and rotation
- Password hashing with bcrypt
- Protected API endpoints with dependency injection

### API Security
- Rate limiting on login endpoints (5 attempts/minute)
- Request body validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM

### Infrastructure Security
- Content Security Policy (CSP) headers
- CORS configuration with environment-aware settings
- X-Content-Type-Options, X-Frame-Options headers
- HSTS headers in production

### Production Hardening
- Debug mode disabled in production
- OpenAPI/Swagger docs disabled in production
- Error messages sanitized in production
- No sensitive data in logs

## 📊 Performance & Load Capacity

### Current Architecture Limits

| Metric | Current Estimate |
|--------|------------------|
| Monitored APIs | Up to 500 endpoints per instance |
| Monitoring Checks | ~10,000 checks/day per instance |
| Concurrent Users | 50-100 active users |
| Response Time | < 200ms for API calls |

### Scalability Recommendations

For handling **10,000+ monitored APIs** and **100,000+ checks/day**:

1. **Database**:
   - Switch from SQLite to PostgreSQL
   - Implement database read replicas
   - Add connection pooling (PgBouncer)

2. **Monitoring Engine**:
   - Use Redis queue for distributed health checks
   - Implement horizontal scaling with multiple workers
   - Add message broker (RabbitMQ/Redis Streams)

3. **Caching**:
   - Implement Redis caching for frequently accessed data
   - Cache API responses and metrics

4. **CDN**:
   - Serve static assets via CDN
   - Consider edge computing for health checks

## 🔍 Monitoring System Explanation

### Health Check Flow

1. **Scheduler**: Runs at configured interval (default: 60 seconds)
2. **Health Checker**: Performs HTTP request to each monitored endpoint
3. **Retry Logic**: Up to 3 retries with exponential backoff on failure
4. **Anomaly Detection**: Z-score calculation for response time anomalies
5. **Alert System**: Triggers email notification after 3 consecutive failures
6. **AI Analysis**: Collects failure logs and sends to LLM for insights

### WebSocket Events

- `health_check_complete`: Fired when a health check finishes
- `endpoint_update`: Fired when endpoint status changes
- Real-time dashboard updates without page refresh

## 📖 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (rate limited)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/debug-token` - Debug token (dev only)

### API Endpoints (Protected)
- `GET /api/apis` - List all endpoints
- `POST /api/apis` - Create endpoint
- `GET /api/apis/{id}` - Get endpoint details
- `PUT /api/apis/{id}` - Update endpoint
- `DELETE /api/apis/{id}` - Delete endpoint
- `POST /api/apis/{id}/toggle` - Toggle active status
- `POST /api/apis/{id}/check` - Manual health check

### Monitoring (Protected)
- `GET /api/monitoring/logs` - Get logs
- `GET /api/monitoring/endpoints/{id}/anomalies` - Get anomalies
- `GET /api/monitoring/endpoints/{id}/baseline` - Get baseline
- `POST /api/monitoring/analyze` - Trigger AI analysis

### Metrics (Protected)
- `GET /api/metrics/overview` - Dashboard overview
- `GET /api/metrics/uptime` - Uptime metrics
- `GET /api/metrics/response-time` - Response time series
- `GET /api/metrics/status-codes` - Status code distribution
- `GET /api/metrics/error-rate` - Error rate

## 🤝 Developer Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ai-mon.git
   cd ai-mon
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   
   python -m uvicorn app.main:app --reload
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env with your API URL
   
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Running Tests
```bash
cd backend
pytest tests/ -v
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework
- [React](https://react.dev/) - UI library
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [OpenAI](https://openai.com/) - AI integration

