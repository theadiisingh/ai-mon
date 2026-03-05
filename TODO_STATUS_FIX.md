# Status Fix TODO List

## Objective
Fix monitored API status display - when an API is DOWN, UI must show DOWN (not ACTIVE/UP)

## Tasks

### 1. Backend: Change default status in ApiEndpoint model
- [x] Change `status = Column(String(10), default="UP")` to allow None
- [x] Update api_schema.py to handle nullable status

### 2. Frontend: Handle null/unknown status in ApiTable
- [x] Update StatusBadge.tsx to handle 'unknown' status
- [x] Update ApiTable.tsx to handle null status

### 3. Frontend: Handle null/unknown status in ApiDetailPage
- [x] Update ApiDetailPage.tsx to handle null status

### 4. Verify health check logic
- [x] Verify health_checker.py correctly sets status
- [x] Verify api_service.py correctly updates status

## Changes Made

### backend/app/models/api.py
- Changed `status = Column(String(10), default="UP")` to `status = Column(String(10), nullable=True)`

### frontend/src/components/dashboard/StatusBadge.tsx
- Added 'unknown' status handling with gray styling

### frontend/src/components/dashboard/ApiTable.tsx
- Updated to handle null status from backend - shows "Unknown" badge

### frontend/src/pages/ApiDetailPage.tsx
- Updated to handle null status from backend - shows gray "Unknown" status

### frontend/src/types/api.ts
- Updated comment to clarify null is allowed

## IMPORTANT: Database Migration Required

Since the `status` column was changed from NOT NULL with default "UP" to NULLABLE, you need to:

1. **For development/testing**: Delete the existing `aimon.db` file and restart the backend
2. **For production**: Run: `ALTER TABLE api_endpoints ALTER COLUMN status DROP NOT NULL;`

## Behavior Now

- **New endpoints**: `status = null` → UI shows "Unknown" (gray)
- **After successful health check**: `status = "UP"` → UI shows "UP" (green)
- **After failed health check**: `status = "DOWN"` → UI shows "DOWN" (red)

