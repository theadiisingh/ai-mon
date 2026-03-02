# TODO - Fix Trailing Slash Route Mismatch

## Task
Fix the "Not Found" error when clicking Refresh button on Dashboard page by removing trailing slashes from frontend API calls.

## Steps Completed:
- [x] Analyzed the frontend API calls and backend routes
- [x] Identified trailing slash as the issue (/apis/ vs /apis)

## Steps to Complete:
- [ ] Fix frontend/src/api/apiApi.ts - remove trailing slashes
- [ ] Check and fix frontend/src/api/metricsApi.ts for trailing slashes
- [ ] Check and fix frontend/src/api/authApi.ts for trailing slashes  
- [ ] Verify the fixes work correctly
