# CSP and SPA Fix Plan

## Tasks:
- [x] 1. Update backend/app/core/config.py - Add environment detection (DEV/PROD)
- [x] 2. Create backend/app/middleware/csp.py - CSP middleware with environment awareness
- [x] 3. Update backend/app/main.py - Add CSP middleware and fix SPA fallback
- [x] 4. Update frontend/vite.config.ts - Add proper proxy and CSP handling
- [ ] 5. Test the changes

## Implementation Details:
### CSP Middleware:
- Development: Allow 'unsafe-eval', localhost:3000, localhost:5173
- Production: Strict CSP without eval

### SPA Fallback:
- Ensure catch-all route properly handles frontend routes
- Exclude API routes, static files, health checks

### Environment Detection:
- DEBUG=true = development mode
- DEBUG=false or not set = production mode
- Can also use ENVIRONMENT=development or ENVIRONMENT=production

## Usage:
### Development:
```bash
# Start backend
cd backend && python run_backend.py

# Start frontend
cd frontend && npm run dev
```

### Production:
```bash
# Set environment variable
export ENVIRONMENT=production
# or
set ENVIRONMENT=production

# Build frontend
cd frontend && npm run build

# Start backend
cd backend && python run_backend.py
```

