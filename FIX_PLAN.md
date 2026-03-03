# AI MON - Fix Plan for Authentication and Navigation Issues

## Information Gathered:

### Architecture:
- Frontend: Vite + React + TypeScript (port 3000)
- Backend: FastAPI (port 8000)
- Database: SQLite
- Auth: JWT tokens (access + refresh)
- Proxy: Vite proxies `/api/*` to backend

### Key Files Analyzed:
1. `frontend/src/App.tsx` - Routes with auth protection
2. `frontend/src/context/AuthContext.tsx` - Auth state management
3. `frontend/src/api/axiosClient.ts` - HTTP client with interceptors
4. `frontend/src/pages/LoginPage.tsx` - Login form
5. `frontend/src/pages/RegisterPage.tsx` - Registration form
6. `frontend/src/hooks/useAuth.ts` - Auth hook
7. `backend/app/api/auth.py` - Backend auth endpoints
8. `backend/app/services/auth_service.py` - Auth business logic
9. `backend/app/core/config.py` - App configuration

### Issues Identified:
1. **Race conditions in token refresh** - Multiple components may try to refresh simultaneously
2. **Loading state timing** - Navigation might happen before auth state is fully resolved
3. **Error handling gaps** - Some errors not properly caught/displayed
4. **Token validation on mount** - Initial auth check might fail silently

## Plan:

### Phase 1: Fix Authentication Context
- [x] **frontend/src/context/AuthContext.tsx**
  - Add explicit `isAuthenticated` state tracking
  - Fix token validation on initial load
  - Improve error handling in login/register
  - Add better logging for debugging
  - Ensure user state is properly set after login
  - Added small delay after login to ensure token propagation

### Phase 2: Fix HTTP Client
- [x] **frontend/src/api/axiosClient.ts**
  - Improve 401 handling
  - Add better retry logic
  - Fix token refresh interceptor
  - Added request queue for failed requests during token refresh

### Phase 3: Fix Login/Register Pages
- [x] **frontend/src/pages/LoginPage.tsx**
  - Add better loading state handling
  - Improve error display
  - Add delay before navigation to ensure state propagation
  
- [x] **frontend/src/pages/RegisterPage.tsx**
  - Similar improvements as LoginPage

### Phase 4: Fix App Router
- [x] **frontend/src/App.tsx**
  - Improve route protection logic
  - Add better loading handling
  - Added initial load state to prevent flash of loading

## Dependent Files:
- All changes are in the frontend, backend remains unchanged

## Followup Steps:
1. Test login flow
2. Test registration flow
3. Test protected routes
4. Test logout functionality
