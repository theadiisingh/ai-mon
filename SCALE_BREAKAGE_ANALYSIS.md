# 🔴 What Would Break at Scale

## Quick Answer - The Top 5 Failure Points

| Rank | Component | Breaks At | Symptom |
|------|-----------|-----------|---------|
| 1 | **SQLite Database** | ~1K concurrent writes | "Database locked" errors, request timeouts |
| 2 | **Health Checker** | ~500 endpoints | Sequential processing, O(n) delay |
| 3 | **No Rate Limiting** | Any scale | Brute force attacks, API abuse |
| 4 | **WebSocket Broadcasting** | ~5K connections | Memory exhaustion, connection drops |
| 5 | **AI API Costs** | 10K+ DAU | $500+/month bill from runaway requests |

---

## Detailed Breakdown

### 1️⃣ SQLite Database - FIRST TO FAIL 🔴

**When**: ~1,000 DAU with heavy monitoring

**What Happens**:
```
SQLite supports only ONE writer at a time.

At scale:
- User A's health check wants to write → Acquires lock
- User B's health check wants to write → BLOCKED (waits 5+ seconds)
- User C's health check wants to write → BLOCKED
- ... hundreds of requests queuing up

Result: "database is locked" errors, 30+ second response times
```

**Evidence in Code**:
```python
# backend/app/core/database.py
# Currently uses NullPool in dev, but SQLite has inherent limitations
# Even with connection pooling, SQLite serializes ALL writes
```

---

### 2️⃣ Health Checker - SECOND TO FAIL 🔴

**When**: ~500 monitored endpoints

**What Happens**:
```python
# Current implementation - Sequential processing
# backend/app/monitoring_engine/health_checker.py

async def run_health_checks(self):
    for endpoint in self.endpoints:  # One at a time!
        result = await self.check_endpoint(endpoint)
        await self.save_result(result)
```

**Calculation**:
- 500 endpoints × 30 seconds per check = 15,000 seconds = 4+ hours
- By the time you check endpoint #500, endpoint #1 is already 4 hours stale

**Result**: Monitoring data becomes useless

---

### 3️⃣ No Rate Limiting - SECURITY BREACH 🟠

**When**: Any scale (exploited immediately)

**Attack Vector**:
```
POST /api/auth/login
Body: {"email": "admin@aimon.com", "password": "password123"}
Repeat 10,000 times in 1 minute → Account compromised
```

**Also**:
- Users create 10,000 endpoints each → Server crashes
- Health check interval set to 1 second → External API blocks you + costs explode

---

### 4️⃣ WebSocket Memory Exhaustion 🟠

**When**: ~5,000+ concurrent connections

**What Happens**:
```python
# Each WebSocket connection uses ~1-2MB RAM
# backend/app/core/websocket.py

# Current: Stores ALL connections in memory
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []  # No limit!
```

**Calculation**:
- 5,000 connections × 1.5MB = 7.5GB RAM needed
- Typical VPS has 2-4GB → OOM (Out of Memory) crash

---

### 5️⃣ AI API Cost Explosion 🟠

**When**: Scale or malicious usage

**Scenario**:
```
User creates 1,000 endpoints
All endpoints fail (external API down)
System triggers AI analysis for EACH failure

1,000 endpoints × 60 checks/hour × 24 hours = 1,440,000 checks
AI analysis triggered for each failure

At ~$0.01 per analysis = $14,400 in one day!
```

**Current Code Issue**:
```python
# No limit on AI insights - every failure triggers analysis
# backend/app/services/ai_service.py

async def check_for_anomalies(log: MonitoringLog):
    # NO checks! Immediately triggers AI
    if log.status == CheckStatus.FAILURE:
        await generate_ai_insight(log)  # 💸 Every. Single. Failure.
```

---

## Secondary Failures

### 6️⃣ No Connection Pooling (PostgreSQL mode)

**When**: 100+ concurrent API requests

```
Connection pool exhausted (20 connections)
↓ 
New requests wait 30 seconds for connection
↓
Requests timeout
↓
"Connection refused" errors
```

### 7️⃣ Full Table Scans on Dashboard

**When**: Large dataset (>100K monitoring logs)

```python
# Every dashboard load runs these queries:
endpoints = await db.query(ApiEndpoint).all()  # ALL endpoints
logs = await db.query(MonitoringLog).all()       # ALL logs
insights = await db.query(AIInsight).all()      # ALL insights
```

**Result**: Dashboard takes 10+ seconds to load

### 8️⃣ SSRF Vulnerability

**When**: Attacker discovers they can probe internal network

```
User adds endpoint: http://192.168.1.1/admin
User adds endpoint: http://localhost:5432 (could hit DB)
User adds endpoint: http://169.254.169.254/ (AWS metadata)
```

**Current Code**: No validation preventing this!

---

## Summary Table

| Component | Break Point | Failure Mode | User Impact |
|-----------|-------------|--------------|-------------|
| **SQLite** | 1K writes/sec | Database locks | "Server error" on every request |
| **Health Checker** | 500 endpoints | 4+ hour delay | Stale data |
| **Rate Limiting** | Any | Account takeover | Security breach |
| **WebSocket** | 5K connections | OOM crash | Service down |
| **AI Costs** | 1K failures | Bill shock | Financial loss |
| **Dashboard** | 100K logs | 10s load time | Poor UX |
| **SSRF** | Any | Internal network access | Security breach |

---

## What to Fix FIRST (Priority Order)

1. ✅ **Add Rate Limiting** - Prevents security + cost issues
2. ✅ **Migrate to PostgreSQL** - Fixes database locking
3. ✅ **Parallelize Health Checks** - Fixes monitoring staleness
4. ✅ **Add AI Insight Limits** - Controls costs
5. ✅ **Add WebSocket Limits** - Prevents memory exhaustion
6. ✅ **Fix SSRF** - Security critical

