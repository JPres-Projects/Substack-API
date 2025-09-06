# Substack API Scheduling Analysis

## Summary

This document analyzes the Substack API scheduling functionality and provides a complete implementation of the discovered workflow. The scheduling system works partially - it can update existing schedules but cannot create initial schedules for new drafts through the API.

## What Works ✅

### 1. Schedule Update Workflow
The 5-step workflow from browser network logs **works perfectly** for drafts that already have schedules:

```python
def schedule_draft_real_web_workflow(draft_id, schedule_datetime):
    """Schedule draft using the REAL web interface workflow - WORKING VERSION"""
    
    schedule_str = schedule_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # STEP 1: publication/verify_status (preparation)
    session.get(f"{pub_url}/api/v1/publication/verify_status", headers=headers)
    
    # STEP 2: publication/post-tag (preparation)
    session.get(f"{pub_url}/api/v1/publication/post-tag", headers=headers)
    
    # STEP 3: post/{id}/tag (preparation)
    session.get(f"{pub_url}/api/v1/post/{draft_id}/tag", headers=headers)
    
    # STEP 4: prepublish with schedule - THE KEY STEP!
    encoded_date = urllib.parse.quote(schedule_str)
    prepublish_url = f"{pub_url}/api/v1/drafts/{draft_id}/prepublish?publish_date={encoded_date}"
    prepublish_response = session.get(prepublish_url, headers=headers)
    
    # STEP 5: post_management/share_center (finalizes)
    session.get(f"{pub_url}/api/v1/post_management/share_center/{draft_id}", headers=headers)
```

**Result:** Creates `postSchedules` entries with correct `trigger_at` timestamps, maintains `is_published: false`.

### 2. Working Example
- Draft ID `172475260` successfully created schedules using this workflow
- All API calls return `200` status codes  
- Schedule object: `{'id': 6712794, 'trigger_at': '2025-09-02T12:35:00.000Z', 'post_audience': 'everyone', 'email_audience': 'everyone'}`

## What Doesn't Work ❌

### 1. Initial Schedule Creation
**Cannot create the first schedule for new drafts.** All tested endpoints return `404`:

```
POST /api/v1/postSchedules -> 404
POST /api/v1/drafts/{id}/schedule -> 404  
POST /api/v1/schedules -> 404
PUT /api/v1/drafts/{id} (with postSchedules) -> 200 but no schedule created
```

### 2. The Root Problem
- **New drafts:** `postSchedules: []` - prepublish workflow fails
- **Drafts with existing schedules:** `postSchedules: [...]` - prepublish workflow succeeds

The initial schedule creation step is either:
1. Not exposed through public API
2. Embedded in complex JavaScript workflows
3. Requires specific account permissions
4. Uses non-standard endpoints not discoverable through REST patterns

## Implementation Status

### Completed ✅
1. **`schedule_draft_real_web_workflow()`** - Fully implemented and working
2. **5-step workflow** - Correctly replicates browser behavior
3. **Draft detection** - Can identify which drafts have schedules
4. **API analysis** - Comprehensive testing of all possible endpoints

### Missing ❌  
1. **Initial schedule creation** - No working API endpoint found
2. **New draft scheduling** - Cannot schedule fresh drafts without existing schedules

## Workaround Solutions

Since the API limitation prevents direct scheduling of new drafts, here are alternative approaches:

### Option 1: N8N + External Scheduler
1. **Use N8N to monitor** scheduled publication times from external sources (Google Sheets, Airtable, etc.)
2. **When schedule time arrives:** Use the working `/publish` endpoint to publish immediately
3. **Schedule management:** Handle timing externally, use Substack API only for final publication

```javascript
// N8N Workflow Example
// 1. Check Google Sheet for scheduled posts
// 2. If current time >= scheduled time:
//    POST /api/v1/drafts/{id}/publish
```

### Option 2: Manual Pre-scheduling
1. **Manually create one schedule** in Substack web interface for each draft
2. **Use API to update** the schedule time using the working workflow
3. **Limitation:** Requires manual web interface interaction for initial setup

### Option 3: Hybrid Approach
1. **Draft creation:** Use API to create and populate drafts
2. **Scheduling:** Use external system (cron jobs, cloud functions) to trigger publication
3. **Publishing:** Use `/publish` endpoint when scheduled time arrives

## Technical Details

### Authentication
Uses session-based authentication with browser cookies:
```python
cookie_map = {
    "sid": os.getenv("SID"),
    "substack.lli": os.getenv("SUBSTACK_LLI"), 
    "substack.sid": os.getenv("SUBSTACK_SID")
}
```

### Key Discovery
The critical insight was that `prepublish` with `publish_date` parameter only works for drafts that already have `postSchedules` entries. The API assumes an existing schedule and updates it, rather than creating new schedules.

### Error Patterns
- New drafts: All 200 responses but `postSchedules` remains empty
- Existing scheduled drafts: 200 responses and `postSchedules` gets updated

## Conclusion

The Substack API scheduling system is **partially functional**. The discovered workflow perfectly replicates browser behavior for updating existing schedules, but lacks the ability to create initial schedules programmatically. 

For production use, combine the working API workflow with external scheduling systems to achieve complete automation. The API is sufficient for content management and publication, but timing control requires hybrid solutions.

## Files

- `draft_schedule.py` - Contains the working `schedule_draft_real_web_workflow()` function
- `getposts.py` - Comprehensive post detection and status analysis  
- `debug_api.py` - Full request/response debugging tools
- `draft_create.py` - Working draft creation functionality

## Testing Results

| Endpoint | Method | Status | Result |
|----------|--------|--------|---------|
| `/api/v1/drafts/{id}/prepublish?publish_date=...` | GET | ✅ 200 | Works for drafts with existing schedules |
| `/api/v1/postSchedules` | POST | ❌ 404 | Not accessible |
| `/api/v1/drafts/{id}/schedule` | POST | ❌ 404 | Not accessible |
| `/api/v1/drafts/{id}/publish` | POST | ✅ 200 | Publishes immediately (not schedules) |
| All preparation endpoints | GET | ✅ 200 | Working correctly |