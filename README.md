# AI MON - Smart API Monitoring & Auto Debug Tool

AI MON is a production-ready MVP for real-time API monitoring with AI-powered debugging insights. It provides comprehensive monitoring, anomaly detection, failure analysis, and alerting capabilities.

## Features

- **User Authentication**: JWT-based authentication system
- **API Registration**: Add APIs with URL, HTTP method, monitoring interval, expected status code, and timeout threshold
- **Background Monitoring**: Async monitoring engine that periodically checks registered APIs
- **Data Storage**: Each check stores timestamp, response time, status code, error message, and anomaly flag
- **Anomaly Detection**: Statistical anomaly detection using rolling mean and standard deviation (Z-score method)
- **Repeated Failure Detection**: Tracks consecutive failures
- **AI Integration**: Collects failure logs and sends them to LLM for analysis (with mock mode fallback)
- **Email Alerts**: Sends notifications when APIs fail consecutively (3+ failures)
- **Frontend Dashboard**: Real-time dashboard with:
  - All user APIs display
  - Uptime percentage
  - Average response time
  - Error rate
  - Response time graph
  - Logs table
  - AI insight panel

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy async
- **Authentication**: JWT with python-jose
- **Scheduler**: APScheduler
- **HTTP Client**: httpx
- **AI**: OpenAI (with mock mode fallback)

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query + Context
- **Charts**: Recharts
- **Routing**: React Router

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or use Docker)

### Backend Setup

1. Navigate to the backend directory:
```
bash
cd backend
```

2. Create a virtual environment:
```
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
bash
pip install -r requirements.txt
```

4. Create a `.env` file (copy from example):
```
env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aimon

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI (optional - will use mock mode if not provided)
OPENAI_API_KEY=your-openai-api-key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
MONITORING_INTERVAL_SECONDS=60
```

5. Run the backend server:
```
bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
```
bash
cd frontend
```

2. Install dependencies:
```
bash
npm install
```

3. Create a `.env` file:
```
env
VITE_API_URL=http://localhost:8000/api
```

4. Run the development server:
```
bash
npm run dev
```

The frontend will be available at http://localhost:5173

### Using Docker (Alternative)

1. Navigate to the backend directory:
```
bash
cd backend
```

2. Start the services:
```
bash
docker-compose up -d
```

This will start both PostgreSQL and the backend API.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/refresh` - Refresh access token

### API Endpoints (Protected)
- `GET /api/apis` - List all API endpoints
- `POST /api/apis` - Create a new API endpoint
- `GET /api/apis/{id}` - Get API endpoint details
- `PUT /api/apis/{id}` - Update API endpoint
- `DELETE /api/apis/{id}` - Delete API endpoint
- `POST /api/apis/{id}/toggle` - Toggle endpoint active status
- `POST /api/apis/{id}/check` - Trigger manual health check

### Monitoring (Protected)
- `GET /api/monitoring/logs` - Get monitoring logs
- `GET /api/monitoring/endpoints/{id}/anomalies` - Get anomalies for endpoint
- `GET /api/monitoring/endpoints/{id}/baseline` - Get response time baseline
- `POST /api/monitoring/analyze` - Trigger AI analysis

### Metrics (Protected)
- `GET /api/metrics/overview` - Get metrics overview
- `GET /api/metrics/uptime` - Get uptime metrics
- `GET /api/metrics/response-time` - Get response time series
- `GET /api/metrics/status-codes` - Get status code distribution
- `GET /api/metrics/error-rate` - Get error rate

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgresql://postgres:postgres@localhost:5432/aimon |
| `SECRET_KEY` | JWT secret key | your-secret-key-change-in-production |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |
| `AI_MODEL` | AI model to use | gpt-4 |
| `SMTP_HOST` | Email SMTP host | smtp.gmail.com |
| `SMTP_PORT` | Email SMTP port | 587 |
| `SMTP_USER` | Email username | - |
| `SMTP_PASSWORD` | Email password | - |
| `MONITORING_INTERVAL_SECONDS` | Health check interval | 60 |

## MVP Functionality Checklist

- ✅ User authentication using JWT
- ✅ API registration (URL, method, interval, status code, timeout)
- ✅ Background async monitoring engine
- ✅ Monitoring check storage (timestamp, response time, status code, error, anomaly flag)
- ✅ Statistical anomaly detection (Z-score method)
- ✅ Repeated failure detection
- ✅ AI integration (with mock mode fallback)
- ✅ Email alerts on consecutive failures
- ✅ Frontend dashboard with all required components

## Architecture

```
ai-mon/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI client and prompt templates
│   │   ├── api/             # API routes
│   │   ├── core/            # Config, database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── monitoring_engine/  # Health checker and scheduler
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── requirements.txt
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── api/            # API clients
│   │   ├── components/     # React components
│   │   ├── context/        # React context
│   │   ├── hooks/         # Custom hooks
│   │   ├── pages/          # Page components
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utilities
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## License

MIT
