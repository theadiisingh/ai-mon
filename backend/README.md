# AI MON - Smart API Monitoring & Auto Debug Tool

Production-ready backend for API monitoring with AI-powered insights.

## Features

- **Real-time API Monitoring**: Monitor your APIs with configurable intervals
- **Anomaly Detection**: Automatic detection of unusual response patterns
- **AI-Powered Insights**: Get AI-generated analysis of failures and issues
- **Email Alerts**: Get notified when your APIs go down
- **JWT Authentication**: Secure user authentication
- **RESTful API**: Clean API design with FastAPI

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy (async)
- **Database**: PostgreSQL (production) / SQLite (testing)
- **Authentication**: JWT
- **AI**: OpenAI GPT-4 (with mock mode for development)
- **Scheduling**: APScheduler
- **Testing**: pytest + pytest-asyncio

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (optional, for production)

### Installation

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```
bash
cd backend
pip install -r requirements.txt
```

3. **Set up environment variables**:
```
bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the database** (using Docker):
```
bash
docker-compose up -d
```

5. **Start the server**:
```
bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

### Install test dependencies

Tests are already included in `requirements.txt`. Additional setup:

```
bash
# For testing, we use SQLite in memory
# No additional setup required
```

### Run all tests

```
bash
cd backend
pytest
```

### Run specific test files

```
bash
# Test authentication
pytest tests/test_auth.py

# Test API endpoints
pytest tests/test_api_endpoints.py

# Test monitoring logic
pytest tests/test_monitoring.py

# Test AI service
pytest tests/test_ai_service.py
```

### Run with coverage

```
bash
pytest --cov=app --cov-report=html
```

### Test options

```
bash
# Run with verbose output
pytest -v

# Run only unit tests (exclude integration)
pytest -m "not integration"

# Run with detailed traceback
pytest --tb=long

# Stop on first failure
pytest -x
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── apis.py      # API endpoint management
│   │   ├── monitoring.py # Monitoring endpoints
│   │   ├── metrics.py   # Metrics endpoints
│   │   └── users.py    # User management
│   ├── core/            # Core configuration
│   │   ├── config.py   # Settings
│   │   ├── database.py # Database setup
│   │   ├── security.py # JWT & password handling
│   │   └── dependencies.py # FastAPI dependencies
│   ├── models/          # SQLAlchemy models
│   │   ├── user.py
│   │   ├── api.py
│   │   ├── monitoring_log.py
│   │   └── ai_insight.py
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── api_service.py
│   │   ├── monitoring_service.py
│   │   ├── ai_service.py
│   │   ├── anomaly_service.py
│   │   └── email_service.py
│   ├── ai/             # AI module
│   │   ├── llm_client.py
│   │   └── prompt_templates.py
│   ├── monitoring_engine/ # Monitoring scheduler
│   │   ├── scheduler.py
│   │   ├── task_manager.py
│   │   └── health_checker.py
│   └── utils/          # Utilities
│       ├── logger.py
│       └── helpers.py
├── tests/              # Test suite
│   ├── conftest.py     # Test fixtures
│   ├── test_auth.py    # Authentication tests
│   ├── test_api_endpoints.py # API CRUD tests
│   ├── test_monitoring.py # Monitoring tests
│   └── test_ai_service.py # AI service tests
├── .env.example       # Environment template
├── requirements.txt   # Python dependencies
├── pytest.ini        # Pytest configuration
└── docker-compose.yml # Docker services
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `SECRET_KEY` | JWT secret key | (required) |
| `OPENAI_API_KEY` | OpenAI API key for AI features | (empty = mock mode) |
| `SMTP_*` | Email configuration | (optional) |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token

### API Endpoints
- `GET /api/apis/` - List user's APIs
- `POST /api/apis/` - Create API endpoint
- `GET /api/apis/{id}` - Get API details
- `PUT /api/apis/{id}` - Update API
- `DELETE /api/apis/{id}` - Delete API
- `POST /api/apis/{id}/toggle` - Toggle active status
- `POST /api/apis/{id}/pause` - Pause monitoring

### Monitoring
- `GET /api/monitoring/logs` - Get monitoring logs
- `GET /api/monitoring/logs/{id}` - Get specific log
- `GET /api/monitoring/endpoints/{id}/anomalies` - Get anomalies
- `POST /api/monitoring/analyze` - Trigger AI analysis

### Metrics
- `GET /api/metrics/overview` - Get metrics overview
- `GET /api/metrics/uptime/{endpoint_id}` - Get uptime data
- `GET /api/metrics/response-time/{endpoint_id}` - Get response time data

## Development Notes

### Mock AI Mode

When `OPENAI_API_KEY` is not set, the AI service runs in mock mode. This is useful for:
- Development without OpenAI API key
- Testing without external dependencies
- Demonstrating functionality

### Database Indexes

The following indexes are automatically created:
- `users.email` - Unique index for login
- `users.username` - Unique index
- `api_endpoints.user_id` - For user's API queries
- `monitoring_logs.api_endpoint_id` - For log queries
- `monitoring_logs.checked_at` - For time-based queries

### Running in Production

1. Set `DEBUG=False`
2. Use strong `SECRET_KEY`
3. Configure PostgreSQL
4. Set up reverse proxy (nginx)
5. Use proper CORS settings
