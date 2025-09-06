# getposts.py - Systematische Suche nach ALLEN Posts/Drafts/Schedules
import os
import requests
from datetime import datetime
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

def get_all_posts():
    """Systematische Suche nach ALLEN Post-Arten mit verschiedenen Endpoints und Parametern"""
    
    all_found_posts = {}  # Dict um Duplikate zu vermeiden
    
    print("=== SYSTEMATISCHE POST-SUCHE ===\n")
    
    # Alle möglichen Endpoints mit verschiedenen Parametern
    endpoints_to_try = [
        # Basic endpoints
        "/api/v1/drafts",
        "/api/v1/posts", 
        "/api/v1/archive",
        
        # Special: Individual drafts (to get postSchedules)
        "INDIVIDUAL_DRAFTS",
        
        # Mit verschiedenen Parametern
        "/api/v1/posts?published=true",
        "/api/v1/posts?published=false", 
        "/api/v1/posts?scheduled=true",
        "/api/v1/posts?draft=true",
        "/api/v1/posts?status=draft",
        "/api/v1/posts?status=published",
        "/api/v1/posts?status=scheduled",
        "/api/v1/posts?all=true",
        "/api/v1/posts?include_drafts=true",
        
        # Andere mögliche Endpoints
        "/api/v1/publication/posts",
        "/api/v1/publication/drafts", 
        "/api/v1/publication/archive",
        "/api/v1/user/posts",
        "/api/v1/user/drafts",
        "/api/v1/me/posts",
        "/api/v1/dashboard/posts",
        
        # Spezielle Schedule-Endpoints
        "/api/v1/scheduled",
        "/api/v1/queue",
        "/api/v1/publication/scheduled",
    ]
    
    current_time = datetime.now()
    
    for endpoint in endpoints_to_try:
        if endpoint == "INDIVIDUAL_DRAFTS":
            print("--- TESTING INDIVIDUAL_DRAFTS ---")
            # First get all draft IDs, then fetch each individually to get postSchedules
            try:
                drafts_response = session.get(f"{pub_url}/api/v1/drafts")
                if drafts_response.status_code == 200:
                    drafts = drafts_response.json()
                    print(f"Found {len(drafts)} drafts to check individually")
                    
                    for draft in drafts:
                        if 'id' in draft:
                            draft_id = draft['id']
                            individual_url = f"{pub_url}/api/v1/drafts/{draft_id}"
                            
                            try:
                                individual_response = session.get(individual_url)
                                if individual_response.status_code == 200:
                                    item = individual_response.json()
                                    post_id = item['id']
                                    
                                    # Sammle alle relevanten Daten
                                    post_info = {
                                        'id': post_id,
                                        'endpoint': f"INDIVIDUAL_DRAFTS/{draft_id}",
                                        'title': item.get('title') or item.get('draft_title', 'NO TITLE'),
                                        'is_published': item.get('is_published'),
                                        'post_date': item.get('post_date'),
                                        'draft_updated_at': item.get('draft_updated_at'),
                                        'updated_at': item.get('updated_at'),
                                        'postSchedules': item.get('postSchedules', []),
                                        'status': 'UNKNOWN'
                                    }
                                    
                                    # Bestimme Status basierend auf Daten
                                    # FIRST: Check for postSchedules (das ist der echte Schedule!)
                                    if post_info['postSchedules']:
                                        try:
                                            schedule = post_info['postSchedules'][0]  # First schedule
                                            trigger_at = schedule.get('trigger_at')
                                            if trigger_at:
                                                schedule_dt = datetime.fromisoformat(trigger_at.replace('Z', '+00:00'))
                                                post_info['schedule_date'] = trigger_at
                                                post_info['status'] = 'SCHEDULED'
                                        except:
                                            post_info['status'] = 'SCHEDULE_ERROR'
                                    elif item.get('post_date'):
                                        try:
                                            post_dt = datetime.fromisoformat(item['post_date'].replace('Z', '+00:00'))
                                            if item.get('is_published'):
                                                if post_dt > current_time:
                                                    post_info['status'] = 'SCHEDULED'
                                                else:
                                                    post_info['status'] = 'PUBLISHED'
                                            else:
                                                post_info['status'] = 'SCHEDULED'
                                        except:
                                            post_info['status'] = 'DATE_ERROR'
                                    elif item.get('is_published'):
                                        post_info['status'] = 'PUBLISHED'
                                    else:
                                        post_info['status'] = 'DRAFT'
                                    
                                    all_found_posts[post_id] = post_info
                                    print(f"  -> {post_info['status']}: {post_info['title']}")
                                    
                            except Exception as e:
                                print(f"Error fetching individual draft {draft_id}: {e}")
            except Exception as e:
                print(f"Error getting drafts list: {e}")
            print()
            continue
        
        url = f"{pub_url}{endpoint}"
        print(f"--- TESTING {endpoint} ---")
        
        try:
            response = session.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if isinstance(data, list):
                        print(f"Found {len(data)} items")
                        for item in data:
                            if isinstance(item, dict) and 'id' in item:
                                post_id = item['id']
                                
                                # Sammle alle relevanten Daten
                                post_info = {
                                    'id': post_id,
                                    'endpoint': endpoint,
                                    'title': item.get('title') or item.get('draft_title', 'NO TITLE'),
                                    'is_published': item.get('is_published'),
                                    'post_date': item.get('post_date'),
                                    'draft_updated_at': item.get('draft_updated_at'),
                                    'updated_at': item.get('updated_at'),
                                    'postSchedules': item.get('postSchedules', []),
                                    'status': 'UNKNOWN'
                                }
                                
                                # Bestimme Status basierend auf Daten
                                # FIRST: Check for postSchedules (das ist der echte Schedule!)
                                if post_info['postSchedules']:
                                    try:
                                        schedule = post_info['postSchedules'][0]  # First schedule
                                        trigger_at = schedule.get('trigger_at')
                                        if trigger_at:
                                            schedule_dt = datetime.fromisoformat(trigger_at.replace('Z', '+00:00'))
                                            post_info['schedule_date'] = trigger_at
                                            post_info['status'] = 'SCHEDULED'
                                    except:
                                        post_info['status'] = 'SCHEDULE_ERROR'
                                elif item.get('post_date'):
                                    try:
                                        post_dt = datetime.fromisoformat(item['post_date'].replace('Z', '+00:00'))
                                        if item.get('is_published'):
                                            if post_dt > current_time:
                                                post_info['status'] = 'SCHEDULED'
                                            else:
                                                post_info['status'] = 'PUBLISHED'
                                        else:
                                            post_info['status'] = 'SCHEDULED'
                                    except:
                                        post_info['status'] = 'DATE_ERROR'
                                elif item.get('is_published'):
                                    post_info['status'] = 'PUBLISHED'
                                else:
                                    post_info['status'] = 'DRAFT'
                                
                                all_found_posts[post_id] = post_info
                                print(f"  -> {post_info['status']}: {post_info['title']}")
                    
                    elif isinstance(data, dict):
                        print(f"Dict response with keys: {list(data.keys())}")
                        if 'id' in data:
                            print(f"Single post found: {data.get('title', 'NO TITLE')}")
                    
                except Exception as e:
                    print(f"JSON parse error: {e}")
                    # Check if response contains useful text
                    if len(response.text) < 200:
                        print(f"Response text: {response.text}")
            else:
                print(f"HTTP Error: {response.status_code}")
                if response.status_code == 403:
                    print("  -> Access denied")
                elif response.status_code == 404:
                    print("  -> Endpoint not found")
                    
        except Exception as e:
            print(f"Request error: {e}")
        
        print()
    
    return all_found_posts

def display_summary(all_posts):
    """Zeige schöne Zusammenfassung aller gefundenen Posts"""
    
    print("=" * 80)
    print("ZUSAMMENFASSUNG ALLER GEFUNDENEN POSTS")
    print("=" * 80)
    
    if not all_posts:
        print("❌ KEINE POSTS GEFUNDEN!")
        return
    
    # Gruppiere nach Status
    by_status = {}
    for post in all_posts.values():
        status = post['status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(post)
    
    print(f"Insgesamt {len(all_posts)} eindeutige Posts gefunden")
    print(f"Status-Verteilung: {dict([(k, len(v)) for k, v in by_status.items()])}")
    print()
    
    current_time = datetime.now()
    
    for status, posts in by_status.items():
        print(f"--- {status} ({len(posts)}) ---")
        
        for post in sorted(posts, key=lambda x: x.get('post_date') or x.get('draft_updated_at') or ''):
            print(f"ID: {post['id']}")
            print(f"  Title: {post['title']}")
            print(f"  Status: {post['status']}")
            
            # Show scheduling info
            if post.get('schedule_date'):
                try:
                    schedule_dt = datetime.fromisoformat(post['schedule_date'].replace('Z', '+00:00'))
                    if schedule_dt > current_time:
                        print(f"  SCHEDULED FOR: {schedule_dt.strftime('%Y-%m-%d %H:%M')} (in {(schedule_dt - current_time).total_seconds()/3600:.1f} hours)")
                    else:
                        print(f"  Was scheduled for: {schedule_dt.strftime('%Y-%m-%d %H:%M')} (should be published now)")
                except:
                    print(f"  Schedule date: {post['schedule_date']} (parse error)")
            elif post['post_date']:
                try:
                    post_dt = datetime.fromisoformat(post['post_date'].replace('Z', '+00:00'))
                    if post_dt > current_time:
                        print(f"  SCHEDULED FOR: {post_dt.strftime('%Y-%m-%d %H:%M')} (in {(post_dt - current_time).total_seconds()/3600:.1f} hours)")
                    else:
                        print(f"  Published: {post_dt.strftime('%Y-%m-%d %H:%M')}")
                except:
                    print(f"  Post date: {post['post_date']} (parse error)")
                    
            # Show postSchedules info if available
            if post.get('postSchedules'):
                print(f"  Schedule info: {post['postSchedules']}")
            
            if post['draft_updated_at']:
                print(f"  Last updated: {post['draft_updated_at']}")
            
            print(f"  Found in: {post['endpoint']}")
            print()

def find_missing_posts():
    """Versuche herauszufinden warum Posts fehlen könnten"""
    
    print("=" * 80)
    print("DIAGNOSE: WARUM FEHLEN POSTS?")
    print("=" * 80)
    
    # Test verschiedene Header-Kombinationen
    test_headers = [
        {"Accept": "application/json"},
        {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
        {"Accept": "*/*", "X-Requested-With": "XMLHttpRequest"},
        {"Accept": "application/json", "Cache-Control": "no-cache"},
    ]
    
    for i, headers in enumerate(test_headers):
        print(f"\n--- TEST {i+1}: Headers {headers} ---")
        
        test_session = requests.Session()
        test_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": pub_url,
        })
        test_session.headers.update(headers)
        
        # Set cookies
        for k, v in cookie_map.items():
            if v:
                test_session.cookies.set(k, v, domain=".substack.com")
        
        try:
            response = test_session.get(f"{pub_url}/api/v1/posts")
            print(f"Posts endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Found {len(data)} posts")
                
            response = test_session.get(f"{pub_url}/api/v1/drafts") 
            print(f"Drafts endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Found {len(data)} drafts")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Current time: {datetime.now()}")
    print(f"Publication: {pub_url}\n")
    
    # Hauptsuche
    all_posts = get_all_posts()
    
    # Zusammenfassung
    display_summary(all_posts)
    
    # Diagnose falls zu wenig gefunden
    if len(all_posts) < 5:  # Du hast gesagt 5 Posts total
        find_missing_posts()