# TODO: Fix AI Insight DateTime to Match Local Time

## Task
Fix the date/time displayed in AI Intelligence insights to match user's local time.

## Root Cause
- Backend uses `datetime.utcnow` which creates naive datetime (no timezone info)
- When frontend receives this, JavaScript Date interprets it incorrectly

## Solution
Change backend to use timezone-aware datetime (`datetime.now(timezone.utc)`)

## Steps
- [x] 1. Analyze codebase and understand the issue
- [x] 2. Update AIInsight model to use timezone-aware datetime
- [x] 3. Update MonitoringLog model for consistency
- [x] 4. Verify the fix works

## Files Edited
1. `backend/app/models/ai_insight.py` - Changed datetime.utcnow to datetime.now(timezone.utc)
2. `backend/app/models/monitoring_log.py` - Same change for consistency

## Summary
The fix is complete. The backend now stores timestamps with proper UTC timezone information. When the frontend receives these timestamps (e.g., "2024-01-15T10:30:00+00:00"), JavaScript's Date object will correctly interpret them as UTC and convert them to the user's local time when displaying via the `formatDateTime()` function.

