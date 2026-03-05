# 🏗 Architecture Stress-Test Report
# AI MON - Smart API Monitoring & Auto Debug Tool

Generated based on comprehensive codebase analysis.

---

# 1️⃣ Schema Stress Test

## Step 1: Current Database Schema

### Core Entities

```
Users Table
├── id (PK, Integer, Indexed)
├── email (Unique, Indexed)
├── username (Unique, Indexed)
├── hashed_password
├── full_name
├── is_active (Boolean)
├── is_superuser (Boolean)
├── created_at (DateTime with timezone)
└── updated_at (DateTime with timezone)

API Endpoints Table
├── id (PK, Integer, Indexed)
├── user_id (FK → Users.id, Indexed)
├── name
├── url (VARCHAR 2048)
├── method (ENUM: GET, POST, PUT, DELETE, PATCH)
├── headers (JSON Text)
├── body (JSON Text)
├── expected_status_code
├── timeout_seconds
├── interval_seconds
├── is_active (Boolean)
├── is_paused (Boolean)
├── status (VARCHAR 10: "UP", "DOWN", None)
├── last_status_code
├── last_response_time (Float, ms)
├── last_checked_at (DateTime)
├── uptime_percentage (Float)
├── total_checks (Integer)
├── successful_checks (Integer)
├── failed_checks (Integer)
├── created_at
└── updated_at

Monitoring Logs Table
├── id (PK, Integer, Indexed)
├── api_endpoint_id (FK → API Endpoints.id, Indexed)
├── user_id (FK → Users.id, Indexed)
├── status (ENUM: SUCCESS, FAILURE, TIMEOUT, ERROR)
├── status_code
├── response_time (Float, ms)
├── error_message (Text)
├── response_body (Text - truncated)
├── checked_at (DateTime with timezone, Indexed)
├── is_anomaly (Boolean)
├── anomaly_score (Float)
├── request_method
└── request_url (VARCHAR 2048)

AI Insights Table
├── id (PK, Integer, Indexed)
├── api_endpoint_id (FK → API Endpoints.id, Indexed)
├── user_id (FK → Users.id, Indexed)
├── insight_type (ENUM)
├── severity (ENUM)
├── title (VARCHAR 500)
├── summary (Text)
├── possible_causes (JSON Text)
├── suggested_steps (JSON Text)
├── triggered_by_log_id (FK → Monitoring Logs.id)
├── related_logs_summary (Text)
├── confidence_score (Float 0-1)
├── model_used (VARCHAR 100)
├── tokens_used (Integer)
├── is_read (VARCHAR 20)
├── is_resolved (Boolean)
├── created_at
└── resolved_at
```

### Relationships

- **User → API Endpoints**: One-to-Many (user_id FK)
- **User → Monitoring Logs**: One-to-Many (user_id FK)
- **User → AI Insights**: One-to-Many (user_id FK)
- **API Endpoints → Monitoring Logs**: One-to-Many (api_endpoint_id FK)
- **API Endpoints → AI Insights**: One-to-Many (api_endpoint_id FK)
- **Monitoring Logs → AI Insights**: One-to-Many (triggered_by_log_id FK)

### Indexing Strategy (Current)
- Primary keys (id) on all tables
- Foreign keys on all relationship columns
- `email`, `username` on Users
- `checked_at` on Monitoring Logs
- `status` on Monitoring Logs

---

## Step 2: Simulated 10,000 Daily Active Users

### Structural Weaknesses

| Issue | Severity | Description |
|-------|----------|-------------|
| **SQLite Limitations** | 🔴 Critical | SQLite has write-locking issues. At 10K DAU with concurrent monitoring, write contention will be severe. |
| **Missing Composite Indexes** | 🟠 High | No composite indexes on (user_id, status), (user_id, created_at) - common query patterns unoptimized |
| **Full Table Scans on Metrics** | 🟠 High | Uptime percentage calculation requires scanning all logs per endpoint |
| **No Connection Pooling (SQLite)** | 🟠 High | NullPool used in dev, but SQLite can't handle connection pooling properly anyway |
| **AI Insights Table Bloat** | 🟡 Medium | No cleanup mechanism - insights accumulate forever |
| **Response Body Storage** | 🟡 Medium | Storing full response body in monitoring_logs can bloat storage quickly |
| **No Pagination on Logs** | 🟡 Medium | Potential for huge result sets on log queries |

### Bottlenecks

1. **Monitoring Check Concurrency**
   - With 10K users, assume avg 10 endpoints per user = 100K endpoints
   - Current: Sequential health checks with configurable intervals
   - At 60-second intervals: ~1,667 checks/second required
   - **Bottleneck**: Single-threaded health checker won't scale

2. **Database Write Throughput**
   - Each check = 1 MonitoringLog insert + 1 APIEndpoint update
   - 100K checks/day = 200K writes minimum
   - SQLite max ~100 writes/second under optimal conditions
   - **Bottleneck**: Write throughput insufficient

3. **AI Insight Generation**
   - Each failed check *could* trigger AI analysis
   - At 1% failure rate = 1K potential AI calls/day
   - **Bottleneck**: OpenAI API rate limits and costs

4. **WebSocket Broadcasting**
   - All connected clients receive all updates
   - **Bottleneck**: No per-user/endpoint filtering

### Redundant Relationships

- Storing `user_id` in both `MonitoringLog` AND `AIInsight` when it can be derived from `api_endpoint_id`
- `uptime_percentage`, `total_checks`, `successful_checks`, `failed_checks` fields on ApiEndpoint are cached/denormalized - good for read performance but adds update complexity

### Risk of Write Amplification

1. **Health Check Updates**: Each health check updates:
   - MonitoringLog (INSERT)
   - ApiEndpoint: status, last_status_code, last_response_time, last_checked_at, uptime_percentage, total_checks, successful_checks, failed_checks (9 fields UPDATE)

2. **AI Insight Creation**: Each insight:
   - AIInsight (INSERT)
   - Optional: Update previous unread insights to "read"

---

## Step 3: Schema Improvements for Scale

### Immediate Recommendations

```sql
-- Add composite indexes for common query patterns
CREATE INDEX idx_monitoring_logs_user_status 
ON monitoring_logs(user_id, status);

CREATE INDEX idx_monitoring_logs_user_created 
ON monitoring_logs(user_id, checked_at DESC);

CREATE INDEX idx_api_endpoints_user_status 
ON api_endpoints(user_id, status);

CREATE INDEX idx_ai_insights_user_read 
ON ai_insights(user_id, is_read);

-- Add partial indexes for active records
CREATE INDEX idx_active_endpoints 
ON api_endpoints(user_id) 
WHERE is_active = 1 AND is_paused = 0;

-- Add covering indexes for dashboard queries
CREATE INDEX idx_monitoring_logs_dashboard 
ON monitoring_logs(api_endpoint_id, checked_at DESC) 
INCLUDE (status, response_time, status_code);
```

### Structural Changes for 100K+ Users

1. **Shard by User ID**
   - Partition monitoring_logs by user_id ranges
   - Reduces index size per partition

2. **Timeseries Optimization**
   - Use TimescaleDB extension for PostgreSQL
   - Automatic partitioning by time

3. **Denormalization for Read Performance**
   - Add `avg_response_time_24h`, `avg_response_time_7d` to ApiEndpoint
   - Precomputed metrics vs. on-the-fly calculation

4. **Archive Old Data**
   - Move monitoring logs > 30 days to cold storage
   - Keep only aggregated metrics in main table

5. **Separate Write and Read Replicas**
   - Master for writes
   - Read replicas for dashboard queries

### Code Changes Required

```python
# 1. Add indexes in models
from sqlalchemy import Index

class MonitoringLog(Base):
    # ... existing columns ...
    __table_args__ = (
        Index('idx_monitoring_logs_user_status', 'user_id', 'status'),
        Index('idx_monitoring_logs_user_created', 'user_id', 'checked_at'),
        Index('idx_monitoring_logs_dashboard', 'api_endpoint_id', 'checked_at'),
    )

# 2. Add database migration system (e.g., Alembic)
# 3. Implement connection pooling for PostgreSQL
# 4. Add read replicas support
# 5. Implement caching layer (Redis)
```

---

# 2️⃣ Security Blind Spot Audit

## Current Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (current) / PostgreSQL (supported)
- **Authentication**: JWT with bcrypt password hashing
- **Real-time**: WebSocket
- **AI**: OpenAI API

## Feature Set

1. User registration and authentication
2. JWT-based login with access/refresh tokens
3. API endpoint management (CRUD)
4. Health check monitoring with configurable intervals
5. Real-time status updates via WebSocket
6. AI-powered failure analysis and insights
7. Metrics tracking (uptime %, response time)
8. Email notifications (password reset)

---

## Potential Vulnerabilities

### Authentication & Authorization

| Vulnerability | Risk Level | Description |
|--------------|------------|-------------|
| **Default Secret Key** | 🔴 Critical | Default secret_key in config.py "your-secret-key-change-in-production" - easy to forget changing |
| **No Rate Limiting** | 🔴 Critical | No brute-force protection on login endpoint |
| **No MFA Support** | 🟠 High | Single-factor authentication only |
| **Weak Token Expiration** | 🟠 High | Access token expires in 30 min, but no token rotation mechanism |
| **No Session Invalidation** | 🟡 Medium | Logout doesn't invalidate tokens (stateless JWT) |

### Role Enforcement

| Vulnerability | Risk Level | Description |
|--------------|------------|-------------|
| **No Row-Level Security** | 🔴 Critical | Users can potentially access other users' endpoints via IDOR |
| **Superuser Check Weak** | 🟠 High | is_superuser field exists but not consistently enforced |
| **No API Key System** | 🟡 Medium | All access requires user login - no service-to-service auth |

### Rate Abuse

| Vulnerability | Risk Level | Description |
|--------------|------------|-------------|
| **No Rate Limiting** | 🔴 Critical | Endpoints can be hammered without restriction |
| **No Request Quotas** | 🟠 High | Users can create unlimited endpoints |
| **Health Check DoS** | 🟠 High | Users can set interval to 1 second, overwhelming their own endpoints |
| **AI API Abuse** | 🟠 High | No limit on AI insight generation - potential bill shock |

### Injection Attacks

| Vulnerability | Risk Level | Description |
|--------------|------------|-------------|
| **SQL Injection** | 🟢 Low | SQLAlchemy ORM protects against this |
| **No Input Sanitization** | 🟡 Medium | User-provided URLs in health checks not validated |
| **SSRF Risk** | 🔴 Critical | Users can configure health checks to hit internal network addresses |

### Data Exposure

| Vulnerability | Risk Level | Description |
|--------------|------------|-------------|
| **Debug Mode in Production** | 🔴 Critical | settings.debug may be True in production, exposing stack traces |
| **No PII Encryption** | 🟠 High | Email, names stored in plain text |
| **Response Body Logging** | 🟠 High | Full response bodies stored - could contain sensitive data |
| **No Audit Logging** | 🟡 Medium | No record of who accessed what data |

### Client-Side Trust Issues

| Vulnerability | Risk Level | Description |
|--------------|------------|-------------|
| **CORS Overly Permissive** | 🟠 High | Allows localhost from multiple ports - acceptable for dev |
| **No CSRF Protection** | 🟢 Low | JWT in Authorization header - protected from CSRF |
| **WebSocket No Auth** | 🟠 High | WebSocket accepts connections, auth validated after connect |

---

## Mitigation Strategies

### Critical Fixes (Immediate)

```python
# 1. Force secret key configuration
import os
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise ValueError("SECRET_KEY must be set in production")

# 2. Add rate limiting
from fastapi_limiter import Limiter
from fastapi_limiter.depends import RateLimiter

@app.post("/api/auth/login")
@RateLimiter(times=5, minutes=1)  # 5 attempts per minute
async def login(request: Request, ...):
    ...

# 3. Add SSRF protection
import ipaddress
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    # Block private IP ranges
    try:
        ip = ipaddress.gethostbyname(hostname)
        if ipaddress.ip_address(ip).is_private:
            return False
    except:
        return False
    
    # Block localhost
    if hostname in ('localhost', '127.0.0.1', '0.0.0.0'):
        return False
    
    return True

# 4. Add row-level security check
async def verify_endpoint_access(db: AsyncSession, endpoint_id: int, user_id: int):
    result = await db.execute(
        select(ApiEndpoint).where(
            ApiEndpoint.id == endpoint_id,
            ApiEndpoint.user_id == user_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(403, "Access denied")
```

### High Priority

```python
# 5. Add request quotas
MAX_ENDPOINTS_PER_USER = 100
MIN_INTERVAL_SECONDS = 60

# 6. Add health check timeout limits
MAX_TIMEOUT_SECONDS = 30

# 7. Enable production debug check
if not settings.debug and settings.environment != "production":
    raise ValueError("Debug mode must be False in production")

# 8. Add audit logging
from app.utils.logger import audit_log

async def log_audit(user_id: int, action: str, resource: str):
    audit_log.info(f"user_id={user_id} action={action} resource={resource}")
```

### Medium Priority

```python
# 9. Add IP allowlist for WebSocket
# 10. Add PII encryption for sensitive fields
# 11. Add MFA support (TOTP)
# 12. Add token refresh rotation
# 13. Implement logout with token blacklist
```

---

# 3️⃣ Vendor Lock-In & Migration Audit

## Current Backend Choice

**SQLite (current) + FastAPI**

At 100K users, the following migration challenges arise:

### Migration Challenges

| Challenge | Severity | Description |
|-----------|----------|-------------|
| **Schema Evolution** | 🟠 High | SQLite schema changes require table recreation - downtime needed |
| **Data Migration** | 🟠 High | Migrating 100K users + millions of logs is complex |
| **Type Differences** | 🟡 Medium | SQLite types different from PostgreSQL - potential data issues |
| **Application Code Changes** | 🟡 Medium | Database.py has SQLite-specific code paths |

### Hard-to-Replace Components

| Component | Lock-In Type | Difficulty to Replace |
|-----------|--------------|----------------------|
| **SQLite Database** | Data Storage | Medium - needs ETL pipeline |
| **aiosqlite Driver** | Database Driver | Low - SQLAlchemy abstracts this |
| **OpenAI API** | AI Service | Medium - need to support alternative LLM providers |
| **JWT Secret Key** | Authentication | Low - standard implementation |

### Data Portability Issues

1. **Monitoring Logs**: 
   - Large volume (millions of records)
   - Need time-based partitioning strategy
   - Export to CSV/Parquet for cold storage

2. **AI Insights**:
   - Linked to OpenAI model responses
   - Need schema to support multiple AI providers
   - Tokens used varies by model - need normalization

3. **User Data**:
   - Passwords hashed with bcrypt - portable
   - JWT tokens - standard format

### Vendor Limitations at Scale

| Limitation | Impact |
|------------|--------|
| **SQLite Concurrent Writes** | Max ~100 writes/sec - insufficient for heavy monitoring |
| **SQLite File Size** | Single file - issues > 100GB |
| **No Horizontal Scaling** | Can't scale read replicas |
| **WebSocket Memory** | All connections in memory - scales to ~10K connections |

---

## Recommendations to Reduce Lock-In Risk

### Design for Portability

```python
# 1. Use database-agnostic patterns
# Instead of SQLite-specific features:
# - Avoid: CHECK constraints, partial indexes, JSON1 extension
# - Use: Standard SQLAlchemy ORM, application-level validations

# 2. Abstract AI provider
class LLMProvider(ABC):
    @abstractmethod
    async def generate_insight(self, prompt: str) -> str:
        ...

class OpenAIProvider(LLMProvider):
    ...

class AnthropicProvider(LLMProvider):
    ...

# 3. Use configuration for all external services
# Already done via settings - good!

# 4. Implement data export utilities
async def export_user_data(user_id: int, format: str = "json"):
    # Export all user data for portability
    ...
```

### PostgreSQL Migration Path

```python
# 1. Add Alembic for migrations
# 2. Use SQLAlchemy's asyncpg for PostgreSQL
# 3. Add connection pool configuration

# Recommended: Use a database abstraction layer
# that supports multiple databases
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql+asyncpg://user:pass@localhost/aimon"
)
```

---

# 4️⃣ Cost Explosion Simulation

## Current Backend Setup

- **Database**: SQLite (file-based, no cloud cost)
- **Hosting**: Self-hosted (costs depend on infrastructure)
- **AI**: OpenAI API (pay-per-use)
- **Monitoring**: Self-hosted health checks (compute cost)
- **WebSocket**: Self-hosted (connection handling)

---

## Cost Behavior Analysis

### At 100 DAU

| Component | Cost Driver | Estimated Cost |
|-----------|-------------|----------------|
| **Hosting** | Compute | ~$5-10/month (VPS) |
| **Database** | SQLite (free) | $0 |
| **AI Insights** | ~10 failures/day × 30 days = 300 calls | ~$3-5/month |
| **Bandwidth** | ~1GB/month | ~$1 |
| **Total** | | **$10-20/month** |

### At 1,000 DAU

| Component | Cost Driver | Estimated Cost |
|-----------|-------------|----------------|
| **Hosting** | Compute | ~$20-40/month |
| **Database** | SQLite (free) | $0 |
| **AI Insights** | ~100 failures/day × 30 = 3K calls | ~$30-50/month |
| **Bandwidth** | ~10GB/month | ~$5 |
| **Total** | | **$60-100/month** |

### At 10,000 DAU

| Component | Cost Driver | Estimated Cost |
|-----------|-------------|----------------|
| **Hosting** | Compute (needs upgrade) | ~$100-200/month |
| **Database** | Need PostgreSQL | ~$50-100/month |
| **AI Insights** | ~1K failures/day × 30 = 30K calls | ~$300-500/month |
| **Bandwidth** | ~100GB/month | ~$20 |
| **Redis (caching)** | Optional | ~$20-30/month |
| **Total** | | **$500-900/month** |

---

## Cost Spikes & Sensitivities

### Unexpected Spikes

| Spike Source | Trigger | Impact |
|--------------|---------|--------|
| **AI API Abuse** | User configures 0 interval, all endpoints fail | $100s in hours |
| **AI Prompt Size** | Large response bodies sent to AI | 10x token usage |
| **WebSocket Connections** | 10K concurrent connections | Memory exhaustion |
| **Log Storage** | No retention policy | Disk full |
| **Monitoring Frequency** | Users set 1-second intervals | Server overload |

### Architectural Cost Sensitivities

1. **AI Integration is #1 Cost Driver**
   - Each failed check *could* trigger AI analysis
   - Need intelligent filtering (only significant failures)

2. **Database Write Costs**
   - PostgreSQL: Per-write costs at high volume
   - Connection pool exhaustion

3. **Real-time Updates**
   - WebSocket broadcasting to all clients
   - Could optimize with per-endpoint subscriptions

---

## Cost Optimization Suggestions

### Immediate (Free)

```python
# 1. Limit AI insight generation
MAX_AI_INSIGHTS_PER_DAY = 10  # Per user
AI_INSIGHT_COOLDOWN_HOURS = 24  # Don't repeat similar insights

# 2. Add monitoring frequency limits
MIN_INTERVAL_SECONDS = 60
MAX_INTERVAL_SECONDS = 3600

# 3. Add log retention
async def cleanup_old_logs(days: int = 30):
    """Delete logs older than N days"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    # Delete old logs
```

### Low Cost

```python
# 4. Add Redis caching
# Cache: endpoint status, metrics, user sessions
CACHE_TTL_SECONDS = 60

# 5. Implement request batching for AI
# Batch multiple failures into single AI call

# 6. Add response body size limit
MAX_RESPONSE_BODY_LENGTH = 10000  # chars
```

### Medium Investment

```python
# 7. Implement smart AI triggering
async def should_trigger_ai_analysis(log: MonitoringLog) -> bool:
    """Only trigger for significant failures"""
    return (
        log.status == CheckStatus.FAILURE and
        not log.is_anomaly and  # Don't re-analyze known anomalies
        log.error_message is not None
    )

# 8. Add database read replicas
# For dashboard queries only

# 9. Implement WebSocket room-based updates
# Subscribe to specific endpoints, not broadcast all
```

---

# 5️⃣ Failure Mode Simulation

## Architecture Description

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI   │────▶│  SQLite DB  │
│   (React)   │◀────│   Backend   │◀────│             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  WebSocket  │
                    │   Manager   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Monitoring │
                    │   Engine    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐     │     ┌──────▼──────┐
       │ Health     │     │     │    AI       │
       │ Checker    │     │     │  Service    │
       └──────┬─────┘     │     └──────┬─────┘
              │           │            │
              ▼           ▼            ▼
         [External   [External   [OpenAI]
          APIs]        Web]
```

---

## Failure Mode Analysis

### Traffic Spike Simulation: 10x Normal Load

| Component | Fails First | Impact | Recovery Time |
|----------|-------------|--------|----------------|
| **Database** | 🟢 Last | Write queue buildup | Medium |
| **Health Checker** | 🔴 First | Too many concurrent checks | Fast |
| **WebSocket** | 🟡 Second | Connection drops | Fast |
| **API Endpoints** | 🔴 First | Slow response | Fast |
| **AI Service** | 🟡 Third | Queue buildup | Slow (rate limits) |

### Specific Failure Scenarios

#### 1. Health Checker Overload

**Trigger**: All users set 60-second intervals, spike in active endpoints

**What Happens**:
```
- Task queue fills up
- Health checks queue behind each other  
- Response times degrade
- Monitoring becomes useless (data is stale)
```

**Data Inconsistency**:
- `last_checked_at` becomes unreliable
- `uptime_percentage` inaccurate

**Monitoring Needed**:
- Queue depth metric
- Average check latency
- Failed check count

**Safeguards**:
```python
# Rate limit health checks
MAX_CONCURRENT_CHECKS = 100
check_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CHECKS)

# Add circuit breaker
from circuitbreaker import circuit_breaker

@circuit_breaker(failure_threshold=10, recovery_timeout=30)
async def check_endpoint(endpoint):
    ...
```

---

#### 2. Database Connection Exhaustion

**Trigger**: High concurrent users, many API requests

**What Happens**:
```
- Connection pool exhausted
- New requests timeout
- Health checks fail to log results
- "Database is locked" errors (SQLite)
```

**Data Inconsistency**:
- Monitoring logs lost (not written)
- Endpoint status not updated

**Monitoring Needed**:
- Active connection count
- Query execution time
- "database locked" error rate

**Safeguards**:
```python
# Add connection pool monitoring
engine = create_async_engine(
    database_url,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_pre_ping=True,
)

# Add query timeouts
async def get_db():
    async with AsyncSessionLocal() as session:
        session.execute(query, timeout=10)  # 10 second timeout
```

---

#### 3. WebSocket Connection Flood

**Trigger**: 10K users all connect via WebSocket simultaneously

**What Happens**:
```
- Memory usage spikes
- Connection handling slows
- Some connections dropped
- Frontend shows stale data
```

**Data Inconsistency**:
- Dashboard shows outdated status
- Users think endpoints are down

**Monitoring Needed**:
- Connected client count
- Message queue depth
- Connection drop rate

**Safeguards**:
```python
# Add connection limits
MAX_WS_CONNECTIONS = 5000
ws_connection_semaphore = asyncio.Semaphore(MAX_WS_CONNECTIONS)

# Add heartbeat to detect dead connections
async def ws_heartbeat(websocket):
    while True:
        await asyncio.sleep(30)
        await websocket.send_json({"type": "ping"})

# Use Redis Pub/Sub for multi-instance deployment
```

---

#### 4. AI Service Rate Limiting

**Trigger**: Many endpoint failures → many AI insight requests

**What Happens**:
```
- OpenAI rate limit hit
- Insight generation fails silently
- Users don't get failure analysis
- No data loss, just missing features
```

**Data Inconsistency**:
- No inconsistency, just missing insights

**Monitoring Needed**:
- AI API error rate
- Token usage
- Queue depth for insights

**Safeguards**:
```python
# Add queue with retry
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def generate_insight(prompt: str) -> str:
    return await openai_client.chat.completions.create(...)

# Add rate limiter
ai_request_semaphore = asyncio.Semaphore(10)  # 10 concurrent requests
```

---

#### 5. External API DoS (Self-Induced)

**Trigger**: User configures health check on rate-limited external API with short interval

**What Happens**:
```
- External API blocks requests
- All health checks fail
- User's own endpoints marked as down
- Could get user IP banned
```

**Data Inconsistency**:
- Uptime percentage artificially lowered

**Monitoring Needed**:
- Failed check rate per endpoint
- External API response patterns

**Safeguards**:
```python
# Add rate limiting per endpoint
RATE_LIMIT_PER_ENDPOINT = 60  # requests per minute

# Add intelligent backoff
async def exponential_backoff(attempt: int) -> int:
    return min(2 ** attempt, 3600)  # Max 1 hour

# Add user-agent rotation
HEADERS = {
    "User-Agent": f"AI-MON/{VERSION}"
}
```

---

## Recommended Monitoring & Safeguards

### Critical Metrics to Track

```python
METRICS = {
    # System
    "cpu_usage": Alert if > 80%,
    "memory_usage": Alert if > 85%,
    "disk_usage": Alert if > 90%,
    
    # Database  
    "db_connection_pool_used": Alert if > 80%,
    "db_query_duration_p95": Alert if > 1s,
    "db_lock_wait_time": Alert if > 100ms,
    
    # Application
    "request_duration_p95": Alert if > 2s,
    "error_rate": Alert if > 5%,
    "active_websocket_connections": Alert if > 4500,
    
    # Business
    "health_check_queue_depth": Alert if > 1000,
    "ai_api_error_rate": Alert if > 10%,
    "failed_health_checks_ratio": Alert if > 20%,
}
```

### Circuit Breaker Patterns

```python
from circuitbreaker import circuit

class ExternalServiceCircuit:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.circuit = circuit(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=Exception
        )
    
    @circuit
    async def call(self, func, *args, **kwargs):
        return await func(*args, **kwargs)

# Usage
health_check_circuit = ExternalServiceCircuit("health_checker")
ai_circuit = ExternalServiceCircuit("openai")

@health_check_circuit.circuit
async def check_endpoint(endpoint):
    ...
```

### Graceful Degradation

```python
async def health_check_with_fallback(endpoint):
    try:
        return await check_endpoint(endpoint)
    except Exception as e:
        # Don't fail silently - log it
        logger.warning(f"Health check failed, using cached: {e}")
        
        # Return cached status if available
        cached = await get_cached_status(endpoint.id)
        if cached:
            return cached
        
        # Last resort: mark as unknown
        return {"status": "UNKNOWN", "error": str(e)}
```

---

# 6️⃣ Completion vs Stability Check

## System Design Evaluation

### Does it optimize for Feature Completion or Stability?

**Primary: Feature Completion** ⚠️

The system is heavily optimized for getting features working quickly, with stability as a secondary concern.

---

## Hidden Technical Debt

| Debt Item | Severity | Description |
|-----------|----------|-------------|
| **SQLite in Production** | 🔴 Critical | Using SQLite at scale will cause severe performance issues |
| **No Database Migrations** | 🔴 Critical | Manual migrations in code, error-prone |
| **No Rate Limiting** | 🔴 Critical | System vulnerable to abuse |
| **Debug Mode Default** | 🔴 Critical | Exposes sensitive information |
| **No Connection Pooling** | 🟠 High | SQLite limitation, but unaddressed for PostgreSQL |
| **No Caching Layer** | 🟠 High | Every request hits database |
| **Monolithic Health Checker** | 🟠 High | Single-threaded, no horizontal scaling |
| **No Idempotency Keys** | 🟡 Medium | Duplicate requests could cause issues |
| **Hardcoded Timeouts** | 🟡 Medium | Not configurable per endpoint |

---

## Unscalable Shortcuts

### 1. Synchronous Health Checks

```python
# Current: Sequential checks
for endpoint in endpoints:
    await check_endpoint(endpoint)  # One at a time
```

**Problem**: O(n) time, can't scale with more endpoints

**Fix**: 
```python
# Parallel with semaphore
semaphore = asyncio.Semaphore(100)
async def check_with_limit(endpoint):
    async with semaphore:
        return await check_endpoint(endpoint)

await asyncio.gather(*[check_with_limit(ep) for ep in endpoints])
```

---

### 2. No Caching

```python
# Current: Every dashboard request hits DB
@app.get("/dashboard")
async def get_dashboard(user_id: int):
    endpoints = await db.query(endpoints).all()  # DB every time
    logs = await db.query(logs).all()  # DB every time
    return {"endpoints": endpoints, "logs": logs}
```

**Problem**: No caching means repeated queries

**Fix**:
```python
# Add Redis caching
from redis.asyncio import Redis

redis = Redis()

@app.get("/dashboard")
async def get_dashboard(user_id: int):
    # Try cache first
    cached = await redis.get(f"dashboard:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Query DB
    data = await query_dashboard(user_id)
    
    # Cache for 60 seconds
    await redis.setex(f"dashboard:{user_id}", 60, json.dumps(data))
    return data
```

---

### 3. Full Table Scans for Metrics

```python
# Current: Calculate uptime every time
uptime = sum(1 for log in logs if log.status == SUCCESS) / len(logs)
```

**Problem**: O(n) scan of all logs

**Fix**:
```python
# Precompute and store
class ApiEndpoint(Base):
    uptime_percentage = Column(Float, default=100.0)  # Already exists!
    total_checks = Column(Integer, default=0)
    successful_checks = Column(Integer, default=0)
    # Update incrementally, not from scratch
```

---

### 4. No Pagination

```python
# Current: Return ALL logs
@app.get("/logs")
async def get_logs(endpoint_id: int):
    logs = await db.query(MonitoringLog).all()  # Everything!
```

**Problem**: Memory explosion with large datasets

**Fix**:
```python
@app.get("/logs")
async def get_logs(
    endpoint_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000)
):
    offset = (page - 1) * page_size
    logs = await db.query(MonitoringLog)\
        .where(MonitoringLog.endpoint_id == endpoint_id)\
        .offset(offset)\
        .limit(page_size)\
        .all()
    
    total = await db.count(MonitoringLog.endpoint_id == endpoint_id)
    
    return {"logs": logs, "total": total, "page": page}
```

---

## Poor Separation of Concerns

### 1. Models Contain Business Logic

```python
# Current: Logic in models
class MonitoringLog(Base):
    def calculate_uptime(self):
        # Business logic in model
        ...
```

**Problem**: Tied to ORM, hard to test

**Fix**: Move to service layer
```python
class MetricsService:
    @staticmethod
    def calculate_uptime(logs: List[MonitoringLog]) -> float:
        ...
```

---

### 2. API Routes Mix Concerns

```python
# Current: Routes do too much
@app.post("/api/endpoints")
async def create_endpoint(endpoint: EndpointCreate, db: Session):
    # Validation
    # DB insert
    # Cache invalidation
    # WebSocket broadcast
    # Email notification
    # All in one function!
```

**Fix**: Use use cases / commands
```python
class CreateEndpointUseCase:
    async def execute(self, endpoint: EndpointCreate, user_id: int):
        # Validate
        # Create
        # Notify
        # Return
```

---

### 3. No Clean Architecture Layers

```
Current:
├── app/api/routes.py       # All routes
├── app/models.py           # Models + business logic
├── app/utils.py            # Mixed utilities
```

**Recommended**:
```
app/
├── api/                    # Controllers
│   └── endpoints.py
├── application/           # Use cases / commands
│   ├── create_endpoint.py
│   └── run_health_check.py
├── domain/               # Business logic (pure)
│   ├── entities/
│   └── services/
├── infrastructure/        # External services
│   ├── database/
│   ├── ai/
│   └── notifications/
└── main.py
```

---

## Recommendations for 100x Scale

### Immediate (This Sprint)

1. ✅ **Add Rate Limiting** - Protect against abuse
2. ✅ **Fix Debug Mode** - Don't expose in production
3. ✅ **Add Database Migrations** - Alembic
4. ✅ **Add Basic Caching** - Redis for hot data

### Short-term (Next 2-3 Months)

1. **Migrate to PostgreSQL** - For write throughput
2. **Add Horizontal Scaling** - Multiple health checker workers
3. **Implement Circuit Breakers** - For external services
4. **Add Comprehensive Monitoring** - Metrics + alerting
5. **Implement Pagination** - All list endpoints

### Long-term (6+ Months)

1. **Refactor to Clean Architecture** - Separation of concerns
2. **Add Read Replicas** - Scale dashboard queries
3. **Add Message Queue** - For async processing (Celery/RQ)
4. **Multi-region Deployment** - For global users
5. **Add CDN** - Static assets

---

## Summary

| Category | Rating | Notes |
|----------|--------|-------|
| **Schema Design** | 🟡 Medium | Good for MVP, needs indexes for scale |
| **Security** | 🔴 Needs Work | Critical gaps (no rate limiting, SSRF) |
| **Vendor Portability** | 🟢 Good | SQLAlchemy abstracts DB, AI can swap |
| **Cost Control** | 🟡 Medium | AI is biggest variable cost |
| **Reliability** | 🟡 Medium | Single point of failures, no circuit breakers |
| **Maintainability** | 🔴 Needs Work | No clean architecture, mixed concerns |

**Overall Assessment**: The system is a solid MVP but needs significant hardening before scaling to 100K users. Prioritize security fixes and database scalability.

---

*Report generated for AI MON Architecture Stress-Test*
*Analysis based on codebase review dated 2024*

