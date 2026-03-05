# Frontend Architecture Fix - TODO

## Task
Refactor frontend to be a pure rendering layer with backend as single source of truth.

## Steps

### Step 1: Clean Up formatters.ts ✅
- [x] Remove `calculateAverageUptime()` function (uses .filter() and .reduce())
- [x] Remove `calculateUptimeFromCounts()` function (manual percentage calculation)
- [x] Keep only presentation functions

### Step 2: Create Centralized MetricsContext ✅
- [x] Create `frontend/src/context/MetricsContext.tsx`
- [x] Implement shared metrics state
- [x] Add proper loading/error states

### Step 3: Update DashboardPage ✅
- [x] Remove inline calculations if any remain
- [x] Use backend data directly (already correct)

### Step 4: Verify Components ✅
- [x] ApiDetailPage - already correct
- [x] ApiTable - already correct  
- [x] UptimeChart - already correct

### Step 5: Clean Up ✅
- [x] Add proper TypeScript types
- [x] Build verified - no errors

## Status: COMPLETED ✅

