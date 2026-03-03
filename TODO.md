# AI MON - System Audit & Stabilization Plan

## ROOT CAUSE ANALYSIS

### 🔴 CRITICAL ISSUES FOUND

#### 1. CORS Configuration (CORS-001)
- **Location**: `backend/app/core/config.py`
- **Issue**: Wildcard patterns in CORS origins with `allow_credentials=True` are incompatible
- **Impact**: CORS errors, failed requests from frontend
- **Fix**: Replace wildcard patterns with explicit origins

#### 2. Duplicate Authentication Dependencies (AUTH-001)
- **Location**: Multiple files
- **Issue**: Three different authentication implementations exist:
  - `app/core/dependencies.py` - proper implementation
  - `app/core/security.py` - has get_current_user
  - `app/api/auth.py` - DUPLICATE implementation (different from dependencies.py)
- **Impact**: Inconsistent token validation, potential 401 loops
- **Fix**: Use `app/core/dependencies.py` consistently everywhere

#### 3. Frontend Vite Proxy Double /api Issue (PROXY-001)
- **Location**: `frontend/vite.config.ts` + `frontend/src/api/axiosClient.ts`
- **Issue**: 
  - Vite proxy: `/api` -> `http://localhost:8000`
  - axiosClient baseURL: `/api`
  - Result: `/api/api/...` calls
- **Impact**: 404 errors, API calls fail
- **Fix**: Remove /api prefix from axiosClient or update proxy

#### 4. Refresh Token Flow Issues (AUTH-002)
- **Location**: `backend/app/api/auth.py` refresh endpoint
- **Issue**: 
  - Uses `oauth2_scheme` dependency but expects form data
  - Frontend sends Authorization header + form data
  - Potential mismatch in token parsing
- **Impact**: Token refresh failures, 401 loops
- **Fix**: Make refresh endpoint explicit, not use oauth2_scheme

#### 5. Frontend Token Storage Race Condition (AUTH-003)
- **Location**: `frontend/src/context/AuthContext.tsx`
- **Issue**: 
  - Multiple simultaneous token refresh attempts
  - Auth state updates before token is stored
- **Impact**: Intermittent 401 errors, dashboard load failures
- **Fix**: Ensure token storage before state updates

### 🟡 OTHER ISSUES TO FIX

#### 6. Missing Proper Error Response Structure
- **Location**: Backend auth endpoints
- **Issue**: No consistent error format with error_code
- **Impact**: Harder to debug, inconsistent frontend handling
- **Fix**: Add standardized error responses

## FILES TO MODIFY

### Backend
1. `backend/app/core/config.py` - Fix CORS
2. `backend/app/api/auth.py` - Fix refresh endpoint, use proper dependencies
3. `backend/app/api/users.py` - Verify using correct dependencies
4. `backend/app/api/apis.py` - Verify using correct dependencies

### Frontend  
5. `frontend/src/api/axiosClient.ts` - Fix base URL
6. `frontend/src/context/AuthContext.tsx` - Fix race conditions
7. `frontend/vite.config.ts` - Review proxy config

## EXECUTION ORDER

### Phase 1: Critical Backend Fixes
- [ ] Fix CORS configuration
- [ ] Fix refresh token endpoint
- [ ] Ensure consistent auth dependency usage

### Phase 2: Frontend Fixes
- [ ] Fix axios base URL
- [ ] Fix AuthContext race conditions
- [ ] Add proper error handling

### Phase 3: Testing
- [ ] Test full auth flow (register, login, dashboard)
- [ ] Test token refresh
- [ ] Verify no 401 loops

### Phase 4: Hardening
- [ ] Add global error handlers
- [ ] Add proper logging
- [ ] Verify production readiness
