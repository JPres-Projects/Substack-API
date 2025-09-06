# draft_schedule.py - Schedule Substack drafts
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Setup session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": os.getenv("PUBLICATION_URL"),
    "Content-Type": "application/json"
})

# Set cookies
cookie_map = {
    "sid": os.getenv("SID"),
    "substack.lli": os.getenv("SUBSTACK_LLI"),
    "substack.sid": os.getenv("SUBSTACK_SID")
}
for k, v in cookie_map.items():
    if v:
        session.cookies.set(k, v, domain=".substack.com")

pub_url = os.getenv("PUBLICATION_URL")

def get_drafts():
    """Get all drafts"""
    response = session.get(f"{pub_url}/api/v1/drafts")
    if response.status_code == 200:
        drafts = response.json()
        print(f"Found {len(drafts)} drafts")
        return drafts
    else:
        print(f"Error getting drafts: {response.text}")
        return []

def schedule_draft_real_web_workflow(draft_id, schedule_datetime):
    """Schedule draft using the REAL web interface workflow discovered from network logs"""
    
    # Format datetime for Substack API
    if isinstance(schedule_datetime, str):
        try:
            schedule_dt = datetime.fromisoformat(schedule_datetime.replace('Z', '+00:00'))
        except:
            print(f"Error: Invalid datetime format. Use ISO format like '2024-01-15T10:00:00'")
            return None
    else:
        schedule_dt = schedule_datetime
    
    schedule_str = schedule_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    print(f"Scheduling draft {draft_id} for {schedule_str} using REAL web workflow")
    
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors", 
        "Sec-Fetch-Site": "same-origin"
    }
    
    # STEP 1: publication/verify_status
    print("Step 1: publication/verify_status")
    verify_url = f"{pub_url}/api/v1/publication/verify_status"
    verify_response = session.get(verify_url, headers=headers)
    print(f"  Status: {verify_response.status_code}")
    
    # STEP 2: publication/post-tag
    print("Step 2: publication/post-tag")
    post_tag_url = f"{pub_url}/api/v1/publication/post-tag"
    post_tag_response = session.get(post_tag_url, headers=headers)
    print(f"  Status: {post_tag_response.status_code}")
    
    # STEP 3: post/{id}/tag
    print(f"Step 3: post/{draft_id}/tag")
    tag_url = f"{pub_url}/api/v1/post/{draft_id}/tag"
    tag_response = session.get(tag_url, headers=headers)
    print(f"  Status: {tag_response.status_code}")
    
    # STEP 4: prepublish (like before)
    print(f"Step 4: prepublish with schedule date")
    import urllib.parse
    encoded_date = urllib.parse.quote(schedule_str)
    prepublish_url = f"{pub_url}/api/v1/drafts/{draft_id}/prepublish?publish_date={encoded_date}"
    print(f"  URL: {prepublish_url}")
    prepublish_response = session.get(prepublish_url, headers=headers)
    print(f"  Status: {prepublish_response.status_code}")
    
    if prepublish_response.status_code == 200:
        try:
            data = prepublish_response.json()
            print(f"  Response: {data}")
            
            # CHECK: Does prepublish actually schedule or just validate?
            # Let's check draft status after prepublish but before share_center
            draft_check = session.get(f"{pub_url}/api/v1/drafts/{draft_id}")
            if draft_check.status_code == 200:
                draft_data = draft_check.json()
                print(f"  After prepublish - is_published: {draft_data.get('is_published')}")
                print(f"  After prepublish - postSchedules: {len(draft_data.get('postSchedules', []))} items")
        except Exception as e:
            print(f"  Error processing prepublish response: {e}")
    
    # STEP 5: post_management/share_center (the final step!)
    print(f"Step 5: post_management/share_center/{draft_id}")
    share_center_url = f"{pub_url}/api/v1/post_management/share_center/{draft_id}"
    share_center_response = session.get(share_center_url, headers=headers)
    print(f"  Status: {share_center_response.status_code}")
    
    if share_center_response.status_code == 200:
        try:
            data = share_center_response.json()
            print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            # CHECK: Maybe the schedule info is in this response?
            if isinstance(data, dict):
                if 'is_scheduled' in data:
                    print(f"  is_scheduled: {data.get('is_scheduled')}")
                if 'postSchedule' in data:
                    print(f"  postSchedule: {data.get('postSchedule')}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # CRITICAL: Maybe I need to make a POST request to actually SAVE the schedule?
    print(f"Step 6: Attempting to POST schedule data...")
    
    schedule_data = {
        'post_date': schedule_str,
        'should_send_email': True,
        'audience': 'everyone'
    }
    
    # Try POSTing to the same prepublish endpoint
    post_response = session.post(f"{pub_url}/api/v1/drafts/{draft_id}/prepublish", json=schedule_data, headers=headers)
    print(f"  POST prepublish: {post_response.status_code}")
    if post_response.status_code == 200:
        try:
            post_data = post_response.json()
            print(f"  POST Response: {post_data}")
        except:
            print(f"  POST Response: {post_response.text[:100]}")
    
    # Check schedule after POST
    final_check = session.get(f"{pub_url}/api/v1/drafts/{draft_id}")
    if final_check.status_code == 200:
        final_data = final_check.json()
        print(f"  Final check - postSchedules: {len(final_data.get('postSchedules', []))} items")
        if final_data.get('postSchedules'):
            print(f"  SUCCESS: Schedule created! {final_data['postSchedules']}")
            return True
    
    # CHECK: Did the schedule get created?
    print(f"\nChecking if schedule was created...")
    check_response = session.get(f"{pub_url}/api/v1/drafts/{draft_id}")
    
    if check_response.status_code == 200:
        draft = check_response.json()
        print(f"Draft status:")
        print(f"  is_published: {draft.get('is_published')}")
        print(f"  post_date: {draft.get('post_date')}")
        print(f"  postSchedules: {len(draft.get('postSchedules', []))} schedules")
        
        if draft.get('postSchedules'):
            schedule = draft['postSchedules'][0]
            print(f"  >>> SUCCESS! Schedule created!")
            print(f"  trigger_at: {schedule.get('trigger_at')}")
            return draft
        else:
            print(f"  >>> Schedule not created - workflow incomplete")
            return None
    else:
        print(f"Error checking draft: {check_response.status_code}")
        return None

def schedule_draft_real_web_style(draft_id, schedule_datetime):
    """Set schedule on draft like web interface does (WITHOUT publishing immediately)"""
    
    # Format datetime for Substack API
    if isinstance(schedule_datetime, str):
        # Parse string datetime
        try:
            schedule_dt = datetime.fromisoformat(schedule_datetime.replace('Z', '+00:00'))
        except:
            print(f"Error: Invalid datetime format. Use ISO format like '2024-01-15T10:00:00'")
            return None
    else:
        schedule_dt = schedule_datetime
    
    # Convert to proper format
    schedule_str = schedule_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    print(f"Setting schedule on draft {draft_id} for {schedule_str} (like web interface)")
    
    # FIRST: Get the current draft to preserve all fields
    get_response = session.get(f"{pub_url}/api/v1/drafts/{draft_id}")
    if get_response.status_code != 200:
        print(f"ERROR: Cannot get draft {draft_id}")
        return None
    
    current_draft = get_response.json()
    print(f"Current draft: {current_draft.get('draft_title', 'No title')}")
    
    # METHOD 1: Try to create postSchedules like web interface does
    schedule_payload = {
        "trigger_at": schedule_str,
        "post_audience": "everyone", 
        "email_audience": "everyone"
    }
    
    # Add postSchedules to the draft (like ECHTER SCHEDULE TEST has)
    updated_draft_data = current_draft.copy()
    
    # Remove fields that shouldn't be in PUT
    remove_fields = ['id', 'created_at', 'updated_at', 'draft_created_at', 'draft_updated_at']
    for field in remove_fields:
        updated_draft_data.pop(field, None)
    
    # METHOD 1: Try to find a separate schedule creation endpoint
    print("Trying to create schedule via separate endpoint...")
    
    schedule_create_data = {
        "draft_id": draft_id,
        "trigger_at": schedule_str,
        "post_audience": "everyone",
        "email_audience": "everyone"
    }
    
    # Try different schedule creation endpoints
    for endpoint in ['/api/v1/schedules', '/api/v1/post_schedules', '/api/v1/postschedules', f'/api/v1/drafts/{draft_id}/schedules']:
        try:
            url = f"{pub_url}{endpoint}"
            create_response = session.post(url, json=schedule_create_data)
            print(f"Testing {endpoint}: {create_response.status_code}")
            
            if create_response.status_code == 200:
                print(f"SUCCESS with {endpoint}!")
                return create_response.json()
            elif create_response.status_code not in [404, 403]:
                print(f"  Error: {create_response.text[:100]}")
        except Exception as e:
            print(f"  Exception: {e}")
    
    # METHOD 2: Try PATCH instead of PUT (partial update)
    print("Trying PATCH with minimal data...")
    
    patch_data = {
        "postSchedules": [schedule_payload]
    }
    
    try:
        patch_response = session.patch(f"{pub_url}/api/v1/drafts/{draft_id}", json=patch_data)
        print(f"PATCH: {patch_response.status_code}")
        
        if patch_response.status_code == 200:
            print(f"SUCCESS with PATCH!")
            return patch_response.json()
        else:
            print(f"PATCH Error: {patch_response.text[:100]}")
    except Exception as e:
        print(f"PATCH Exception: {e}")
        
    # METHOD 3: Try PUT with required fields filled
    print("Trying PUT with required fields...")
    
    # Set required fields that were causing validation errors
    updated_draft_data['post_date'] = schedule_str  # Set the schedule date as post_date
    updated_draft_data['slug'] = current_draft.get('slug') or f"draft-{draft_id}"  # Generate slug if missing
    
    # Add the schedule info
    updated_draft_data['postSchedules'] = [schedule_payload]
    
    put_response = session.put(f"{pub_url}/api/v1/drafts/{draft_id}", json=updated_draft_data)
    
    if put_response.status_code == 200:
        print(f"SUCCESS! Draft {draft_id} scheduled for {schedule_str} (NOT published)")
        return put_response.json()
    else:
        print(f"PUT with required fields failed: {put_response.status_code}")
        print(f"Error: {put_response.text[:200]}")
        
        # METHOD 4: Try different approach
        print("All methods failed. The web interface might use a different API...")
        
        # Maybe there's a separate endpoint for creating schedules
        schedule_create_data = {
            "draft_id": draft_id,
            "trigger_at": schedule_str,
            "post_audience": "everyone",
            "email_audience": "everyone"
        }
        
        # Try different schedule creation endpoints
        for endpoint in ['/api/v1/schedules', '/api/v1/post_schedules', '/api/v1/postschedules']:
            try:
                url = f"{pub_url}{endpoint}"
                create_response = session.post(url, json=schedule_create_data)
                if create_response.status_code == 200:
                    print(f"SUCCESS with {endpoint}!")
                    return create_response.json()
            except:
                pass
        
        return None

def schedule_draft(draft_id, schedule_datetime):
    """OLD FUNCTION - PUBLISHES IMMEDIATELY! Use schedule_draft_web_interface_style instead"""
    
    # Format datetime for Substack API
    if isinstance(schedule_datetime, str):
        # Parse string datetime
        try:
            schedule_dt = datetime.fromisoformat(schedule_datetime.replace('Z', '+00:00'))
        except:
            print(f"Error: Invalid datetime format. Use ISO format like '2024-01-15T10:00:00'")
            return None
    else:
        schedule_dt = schedule_datetime
    
    # Convert to proper format
    schedule_str = schedule_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    print(f"WARNING: This will PUBLISH immediately! Use schedule_draft_web_interface_style() instead")
    print(f"Publishing draft {draft_id} for {schedule_str}")
    
    # THE KEY: Use publish endpoint with post_status="scheduled"
    schedule_data = {
        "post_date": schedule_str,
        "should_send_email": True,
        "audience": "everyone",
        "post_status": "scheduled"  # THIS IS THE MAGIC KEY!
    }
    
    response = session.post(f"{pub_url}/api/v1/drafts/{draft_id}/publish", json=schedule_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"SUCCESS! Draft {draft_id} PUBLISHED/SCHEDULED for {schedule_str}")
        return result
    else:
        print(f"FAILED to schedule: {response.text}")
        return None

def list_scheduled_drafts():
    """List all scheduled drafts"""
    drafts = get_drafts()
    scheduled_drafts = []
    
    print("\n=== SCHEDULED DRAFTS ===")
    for draft in drafts:
        post_date = draft.get('post_date')
        if post_date:
            scheduled_drafts.append(draft)
            print(f"Draft ID: {draft['id']}")
            print(f"Title: {draft.get('draft_title', 'Untitled')}")
            print(f"Scheduled for: {post_date}")
            print(f"Status: {draft.get('post_status', 'unknown')}")
            print("-" * 40)
    
    if not scheduled_drafts:
        print("No scheduled drafts found")
    
    return scheduled_drafts

def unschedule_draft(draft_id):
    """Remove scheduling from a draft (make it unpublished draft again)"""
    
    print(f"Unscheduling draft {draft_id}")
    
    # Remove the post_date to unschedule
    unschedule_data = {
        "post_date": None
    }
    
    response = session.put(f"{pub_url}/api/v1/drafts/{draft_id}", json=unschedule_data)
    
    if response.status_code == 200:
        draft = response.json()
        print(f"SUCCESS! Draft {draft_id} unscheduled")
        return draft
    else:
        print(f"FAILED to unschedule: {response.text}")
        return None

def schedule_for_tomorrow(draft_id, hour=9, minute=0):
    """Convenience function to schedule for tomorrow at specific time"""
    tomorrow = datetime.now() + timedelta(days=1)
    schedule_time = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return schedule_draft(draft_id, schedule_time)

def test_real_scheduling_methods(draft_id):
    """Test REAL scheduling methods that actually work"""
    
    future_time = datetime.now() + timedelta(hours=2)
    future_str = future_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    print(f"Testing REAL scheduling for draft {draft_id}")
    print(f"Target time: {future_str}")
    
    # Method 1: Publish with post_status scheduled
    print("\n=== METHOD 1: Publish with post_status=scheduled ===")
    schedule_data1 = {
        "post_date": future_str,
        "should_send_email": True,
        "audience": "everyone",
        "post_status": "scheduled"
    }
    response1 = session.post(f"{pub_url}/api/v1/drafts/{draft_id}/publish", json=schedule_data1)
    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        result = response1.json()
        print(f"SUCCESS! Post scheduled!")
        print(f"Post ID: {result.get('id')}")
        print(f"Post Date: {result.get('post_date')}")
        return result
    else:
        print(f"Response: {response1.text}")
    
    # Method 2: Different date format
    print("\n=== METHOD 2: Different date format ===")
    future_str2 = future_time.isoformat() + "Z"
    schedule_data2 = {
        "post_date": future_str2,
        "should_send_email": True,
        "audience": "everyone"
    }
    response2 = session.post(f"{pub_url}/api/v1/drafts/{draft_id}/publish", json=schedule_data2)
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        result = response2.json()
        print(f"SUCCESS! Post scheduled with ISO format!")
        return result
    else:
        print(f"Response: {response2.text}")
    
    # Method 3: Try with browser headers
    print("\n=== METHOD 3: With browser headers ===")
    session.headers.update({
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    })
    
    response3 = session.post(f"{pub_url}/api/v1/drafts/{draft_id}/publish", json=schedule_data1)
    print(f"Status: {response3.status_code}")
    if response3.status_code == 200:
        result = response3.json()
        print(f"SUCCESS! Headers worked!")
        return result
    else:
        print(f"Response: {response3.text}")
    
    return None

def debug_all_data_structures():
    """Debug ALLE verfügbaren Datenstrukturen um zu verstehen was da ist"""
    
    print("=== COMPLETE DATA STRUCTURE DEBUG ===")
    
    # 1. Alle Drafts komplett ausgeben
    print("\n1. === ALL DRAFTS - COMPLETE DATA ===")
    drafts_response = session.get(f"{pub_url}/api/v1/drafts")
    if drafts_response.status_code == 200:
        drafts = drafts_response.json()
        print(f"Found {len(drafts)} drafts")
        
        for i, draft in enumerate(drafts[:3]):  # Erste 3 Drafts
            print(f"\n--- DRAFT {i+1} (ID: {draft.get('id')}) ---")
            print(f"Title: {draft.get('draft_title', 'No title')}")
            
            # ALLE Keys ausgeben
            print("ALL KEYS:")
            for key in sorted(draft.keys()):
                value = draft[key]
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                try:
                    print(f"  {key}: {type(value)} = {value}")
                except UnicodeEncodeError:
                    print(f"  {key}: {type(value)} = [Unicode content]")
    
    # 2. Alle Posts komplett ausgeben
    print("\n\n2. === ALL POSTS - COMPLETE DATA ===")
    posts_response = session.get(f"{pub_url}/api/v1/posts")
    if posts_response.status_code == 200:
        posts = posts_response.json()
        print(f"Found {len(posts)} posts")
        
        for i, post in enumerate(posts[:3]):  # Erste 3 Posts
            print(f"\n--- POST {i+1} (ID: {post.get('id')}) ---")
            print(f"Title: {post.get('title', 'No title')}")
            
            # ALLE Keys ausgeben
            print("ALL KEYS:")
            for key in sorted(post.keys()):
                value = post[key]
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                try:
                    print(f"  {key}: {type(value)} = {value}")
                except UnicodeEncodeError:
                    print(f"  {key}: {type(value)} = [Unicode content]")
    
    # 3. Schaue nach scheduling-relevanten Feldern
    print("\n\n3. === SCHEDULING-RELATED FIELDS ANALYSIS ===")
    all_items = []
    
    if drafts_response.status_code == 200:
        all_items.extend([('draft', d) for d in drafts_response.json()])
    if posts_response.status_code == 200:
        all_items.extend([('post', p) for p in posts_response.json()])
    
    scheduling_fields = {}
    for item_type, item in all_items:
        for key, value in item.items():
            if any(word in key.lower() for word in ['schedul', 'date', 'time', 'publish', 'status', 'queue']):
                field_key = f"{item_type}_{key}"
                if field_key not in scheduling_fields:
                    scheduling_fields[field_key] = []
                scheduling_fields[field_key].append(value)
    
    print("POTENTIAL SCHEDULING FIELDS:")
    for field, values in scheduling_fields.items():
        unique_values = list(set([str(v) for v in values if v is not None]))[:5]  # Max 5 unique values
        print(f"  {field}: {unique_values}")

def check_for_scheduled_content():
    """Prüfe ob es scheduled content gibt (den du manuell im Web erstellt hast)"""
    
    print("=== CHECKING FOR SCHEDULED CONTENT ===")
    
    # Check ALL endpoints für scheduled content
    endpoints_to_check = [
        "/api/v1/drafts",
        "/api/v1/posts", 
        "/api/v1/scheduled",
        "/api/v1/queue",
        "/api/v1/publication/scheduled",
        "/api/v1/publication/posts"
    ]
    
    for endpoint in endpoints_to_check:
        print(f"\n--- CHECKING {endpoint} ---")
        response = session.get(f"{pub_url}{endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"Found {len(data)} items")
                    for item in data[:2]:  # First 2 items
                        if 'post_date' in item and item['post_date']:
                            print(f"  FOUND POST_DATE: {item['post_date']}")
                        if 'draft_title' in item:
                            print(f"  Draft: {item['draft_title']}")
                        elif 'title' in item:
                            print(f"  Post: {item['title']}")
                else:
                    print(f"Response: {type(data)}")
            except:
                print(f"Response not JSON: {response.text[:100]}...")
        else:
            print(f"Error: {response.text[:100]}...")

def find_real_schedule_endpoint():
    """Find the REAL scheduling endpoint that web interface uses"""
    
    print("=== SEARCHING FOR REAL SCHEDULE ENDPOINT ===")
    
    # Get a draft to test with
    drafts = get_drafts()
    test_draft = None
    for draft in drafts:
        if not draft.get('post_date') and not draft.get('is_published') and not draft.get('postSchedules'):
            test_draft = draft
            break
    
    if not test_draft:
        print("No suitable draft found for testing")
        return
    
    draft_id = test_draft['id']
    print(f"Testing with draft {draft_id}: {test_draft.get('draft_title')}")
    
    from datetime import datetime, timedelta
    future_time = datetime.now() + timedelta(days=1)
    schedule_str = future_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # Test EVERY possible scheduling endpoint
    endpoints_to_test = [
        # Different paths
        f"/api/v1/drafts/{draft_id}/schedule",
        f"/api/v1/posts/{draft_id}/schedule", 
        f"/api/v1/schedules",
        f"/api/v1/post_schedules",
        f"/api/v1/postSchedules",
        f"/api/v1/publication/schedules",
        f"/api/v1/publication/post_schedules",
        
        # Maybe it's a PUT/PATCH to different endpoints
        f"/api/v1/drafts/{draft_id}/set_schedule",
        f"/api/v1/drafts/{draft_id}/plan",
        f"/api/v1/drafts/{draft_id}/delay",
        f"/api/v1/drafts/{draft_id}/queue",
        
        # Maybe it's part of a workflow endpoint
        f"/api/v1/drafts/{draft_id}/prepare_schedule",
        f"/api/v1/drafts/{draft_id}/save_schedule",
    ]
    
    schedule_payload = {
        "draft_id": draft_id,
        "trigger_at": schedule_str,
        "post_audience": "everyone",
        "email_audience": "everyone"
    }
    
    for endpoint in endpoints_to_test:
        url = f"{pub_url}{endpoint}"
        print(f"\n--- TESTING {endpoint} ---")
        
        # Try POST
        try:
            response = session.post(url, json=schedule_payload)
            print(f"POST: {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS! Found the endpoint!")
                try:
                    data = response.json()
                    print(f"Response: {data}")
                    return endpoint, data
                except:
                    print("Success but no JSON response")
                    return endpoint, None
            elif response.status_code not in [404, 403, 405]:
                print(f"Interesting response: {response.text[:100]}")
        except Exception as e:
            print(f"POST error: {e}")
        
        # Try PUT for existing schedule modification
        try:
            put_payload = schedule_payload.copy()
            put_payload['id'] = draft_id  # Maybe needs ID
            
            response = session.put(url, json=put_payload)
            print(f"PUT: {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS with PUT!")
                try:
                    data = response.json()
                    print(f"Response: {data}")
                    return endpoint, data
                except:
                    print("Success but no JSON response")
                    return endpoint, None
        except Exception as e:
            print(f"PUT error: {e}")
        
        # Try PATCH for partial updates
        try:
            patch_payload = {"schedule_date": schedule_str}
            response = session.patch(url, json=patch_payload)
            print(f"PATCH: {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS with PATCH!")
                try:
                    data = response.json()
                    print(f"Response: {data}")
                    return endpoint, data
                except:
                    return endpoint, None
        except:
            pass
    
    print("\n❌ NO WORKING SCHEDULE ENDPOINT FOUND!")
    return None, None

if __name__ == "__main__":
    print("=== TESTING NEW REAL WORKFLOW ===")
    
    # Test the discovered real workflow
    from datetime import datetime, timedelta
    
    # Get a draft to test with - find a truly unpublished one
    drafts_response = session.get(f"{pub_url}/api/v1/drafts")
    if drafts_response.status_code == 200:
        drafts = drafts_response.json()
        test_draft_id = None
        draft_title = None
        
        for draft in drafts:
            # Find a draft that is NOT published and has NO post_date and NO postSchedules
            if (not draft.get('is_published') and 
                not draft.get('post_date') and 
                not draft.get('postSchedules')):
                test_draft_id = draft['id']
                draft_title = draft.get('draft_title', 'NO TITLE')
                print(f"Found clean draft: {test_draft_id} - {draft_title}")
                break
        
        if not test_draft_id:
            print("No unpublished drafts found! All drafts are already published.")
            exit(1)
        
        print(f"Testing with draft {test_draft_id}: {draft_title}")
        
        # Schedule for 2 hours from now
        future_time = datetime.now() + timedelta(hours=2)
        
        result = schedule_draft_real_web_workflow(test_draft_id, future_time)
        
        if result:
            print("SUCCESS! Workflow completed successfully")
            
            # Check if it actually scheduled
            print("\nChecking if draft was scheduled...")
            draft_check = session.get(f"{pub_url}/api/v1/drafts/{test_draft_id}")
            if draft_check.status_code == 200:
                draft_data = draft_check.json()
                print(f"Draft status: published={draft_data.get('is_published')}")
                print(f"Post date: {draft_data.get('post_date')}")
                print(f"Post schedules: {draft_data.get('postSchedules', [])}")
        else:
            print("FAILED: Workflow did not complete successfully")
    else:
        print("No drafts found to test with")