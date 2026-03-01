# AI MON - Production Optimization TODO List

## Phase 1: Codebase Audit & Optimization

### Backend Optimizations

#### 1.1 Remove Duplicate Code & Imports
- [ ] Remove duplicate `get_current_user` in `auth.py` (already exists in `security.py`)
- [ ] Clean up unused imports across all files
- [ ] Remove redundant `UserService` instantiation in auth routes

#### 1.2 Refactor & Decouple
- [ ] Move `get_db` from `database.py` to `dependencies.py`
- [ ] Consolidate error handling patterns in API routes
- [ ] Extract common response schemas

#### 1.3 Ensure Proper Async Usage
- [ ] Review all sync operations in async functions
- [ ] Add `await` where missing
- [ ] Verify httpx client properly async

#### 1.4 Optimize Database Queries
- [ ] Add composite indexes for user_id + created_at
- [ ] Add indexes on foreign keys (api_endpoint_id, user_id)
- [ ] Optimize count queries (use func.count instead of len)
- [ ] Add query optimization hints

#### 1.5 Standardize Error Handling
- [ ] Create unified error response schema
- [ ] Add global exception handler
- [ ] Ensure consistent HTTP status codes

#### 1.6 Improve Logging
- [ ] Implement structured logging with context
- [ ] Add correlation IDs for requests
- [ ] Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

#### 1.7 Environment Variables
- [ ] Add proper validation for sensitive configs
- [ ] Add .env.example file
- [ ] Document required environment variables

### Frontend Optimizations

#### 1.8 Code Quality
- [ ] Add proper TypeScript types for all API responses
- [ ] Add loading states to all async operations
- [ ] Implement error boundaries
- [ ] Add request/response interceptors with retry logic

#### 1.9 Performance
- [ ] Optimize re-renders with useMemo/useCallback
- [ ] Add API response caching
- [ ] Implement proper loading skeletons
- [ ] Optimize chart component rendering

## Phase 2: Backend Testing

### 2.1 Unit Tests
- [ ] Test authentication (login, register, token refresh)
- [ ] Test API creation (CRUD operations)
- [ ] Test monitoring logic (scheduler, health checks)
- [ ] Test anomaly detection
- [ ] Test AI service with mock LLM

### 2.2 Integration Tests
- [ ] Test API registration → monitoring → log storage flow
- [ ] Test repeated failure → AI trigger flow
- [ ] Test email notifications

### 2.3 Mock External Services
- [ ] Mock LLM API calls
- [ ] Mock email sending
- [ ] Mock HTTP requests for health checks

## Phase 3: Monitoring Engine Stability

- [ ] Verify scheduler starts correctly on startup
- [ ] Test concurrent API monitoring
- [ ] Test monitoring tasks don't block main app
- [ ] Test failure handling doesn't crash scheduler
- [ ] Test repeated failures trigger AI logic

## Phase 4: Frontend Testing & Optimization

- [ ] Add unit tests for components
- [ ] Test authentication flows
- [ ] Test API calls and error handling
- [ ] Optimize performance

## Phase 5: Final Stability Checklist

- [ ] Backend starts cleanly
- [ ] Frontend connects properly
- [ ] Monitoring works
- [ ] AI mock works
- [ ] Alerts trigger
- [ ] All tests pass
- [ ] No console errors
- [ ] No unhandled promise rejections
