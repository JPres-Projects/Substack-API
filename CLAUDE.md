# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a fully functional Python-based Substack API client that enables programmatic creation, management, and publishing of Substack posts. Available as both **command-line tools** and **HTTP REST API server**. **Supports multiple Substack accounts** with account-specific environment management. Most core functionality works, with some limitations in scheduling.

## Environment Setup - Multi-Account Support

The project supports multiple Substack accounts with separate environment files:

### Account Structure
- Environment files stored in `env/` directory
- Named as `.account1.env`, `.account2.env`, etc.
- Each account identified by unique `USER_ID`
- All API calls require `user_id` parameter to specify account

### Account Environment Format
Each account file contains:
```
PUBLICATION_URL=https://yourpub.substack.com
USER_ID=your_user_id  
SID=cookie_value
SUBSTACK_LLI=cookie_value
SUBSTACK_SID=cookie_value
```

### Account Management
- List accounts: `GET /accounts`
- Webhook updates: Account-specific via `user_id`
- Automatic account creation when using webhook with new `user_id`

Authentication cookies must be extracted from a browser session where you're logged into Substack.

## What Works ✅

### 1. Draft Creation (`draft_create.py`) - FULLY ENHANCED
- ✅ **Multiple creation modes** - simple text, markup, comprehensive test, rich formatting
- ✅ **User-friendly markup syntax** - create rich content with simple text input
- ✅ **All content types supported** - headings, formatting, lists, quotes, buttons, widgets
- ✅ **File-based input** - reads from `sampleinput/2.txt` for option 2
- ✅ **Proper content structure** - creates valid JSON content format
- ✅ **Byline handling** - correctly sets author information
- ✅ **Error handling** - validates required fields and filters problematic elements

**Usage:** `python draft_create.py`
- Choose from 4 creation modes
- Option 2 reads markup from `sampleinput/2.txt` automatically
- Supports title/subtitle extraction from markup
- **CRITICAL FIX**: Empty text elements with formatting marks were breaking Substack's content parser - now filtered out

### 2. Draft Publishing (`draft_publish.py`)
- ✅ **Interactive draft selection** - lists available drafts with previews
- ✅ **Publishing options** - email sending, audience selection (everyone/paid)
- ✅ **Confirmation workflow** - shows what will be published
- ✅ **Auto-draft creation** - offers to create draft if none exist
- ✅ **Immediate publishing** - publishes drafts instantly

**Usage:** `python draft_publish.py`
- Lists unpublished drafts with ID, title, content preview
- User selects draft and publishing options
- Publishes immediately with confirmation

### 3. Schedule Management (Limited)
- ✅ **Schedule updates** - can modify existing scheduled posts
- ✅ **5-step workflow** - replicates browser scheduling behavior
- ✅ **Working for existing schedules** - `schedule_draft_real_web_workflow()`

### 4. Draft Analysis (`getposts.py`)
- ✅ **Comprehensive post detection** - finds all drafts, published posts, schedules
- ✅ **Status categorization** - DRAFT, PUBLISHED, SCHEDULED analysis
- ✅ **Schedule information** - shows `postSchedules` data with trigger times

## What Doesn't Work ❌

### 1. Initial Schedule Creation
- ❌ **Cannot create first schedule** for new drafts via API
- ❌ **All schedule endpoints return 404** - `/api/v1/postSchedules`, `/api/v1/drafts/{id}/schedule`
- ❌ **prepublish only updates** existing schedules, doesn't create new ones

**Root cause:** The API can manage existing schedules but lacks endpoints to create initial schedules for new drafts.

### 2. Advanced Scheduling Features
- ❌ **Recurring posts** - no API support discovered
- ❌ **Bulk scheduling** - limited to individual posts
- ❌ **Schedule templates** - not available via API

## Core Architecture

### Working Scripts
1. **`draft_create.py`** - Interactive draft creation with title/content prompts
2. **`draft_publish.py`** - Interactive publishing with draft selection and options
3. **`draft_schedule.py`** - Contains `schedule_draft_real_web_workflow()` for existing schedules
4. **`getposts.py`** - Comprehensive post analysis and status checking
5. **`debug_api.py`** - Full request/response debugging tools
6. **`multi_account.py`** - Multi-account environment management utilities
7. **`api_server.py`** - FastAPI server with multi-account support

### Multi-Account System
- Account-specific environment files in `env/` directory (`.account1.env`, `.account2.env`, etc.)
- Each account identified by unique `USER_ID`
- Dynamic account loading based on API `user_id` parameter
- Automatic account creation via webhook for new user_ids
- Account listing and management via API endpoints

### Authentication System  
- Uses session-based authentication with browser cookies per account
- All requests include proper headers and referrer information
- Session cookies: `sid`, `substack.lli`, `substack.sid`
- Account-specific cookie management

### Content Structure
Posts use structured JSON content format:
```json
{
  "type": "doc",
  "content": [
    {
      "type": "paragraph", 
      "content": [
        {"type": "text", "text": "Your content here"}
      ]
    }
  ]
}
```

## Common Development Commands

### 🚀 API Server (Recommended)
```bash
# Start HTTP API server
pip install -r requirements.txt
python api_server.py

# Server runs on: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

### 💻 Command Line Tools  
```bash
# Create new draft (4 modes available)
python draft_create.py

# Publish existing draft interactively  
python draft_publish.py

# Update environment credentials easily
python change_env.py

# Analyze all posts and schedules
python getposts.py

# View markup syntax examples and guide
python docs/markup_examples.py

# Test scheduling workflow (manual browser method)
# Note: API scheduling not available - use browser for initial schedule creation
```

### 🌐 API Usage Examples

## ⚠️ CRITICAL: Windows CMD Usage Instructions
**MUST FOLLOW - Commands will FAIL otherwise:**
1. **Open CMD (NOT PowerShell)** - PowerShell has quote escaping issues
2. **Write COMPLETE command in Notepad first**
3. **Select ALL and copy the entire command** 
4. **Paste into CMD and ONLY THEN press Enter**
5. **NEVER press Enter while typing** - CMD thinks incomplete commands are separate commands

### Working CMD Commands (Multi-Account):
```cmd
# List all accounts
curl "http://localhost:8000/accounts"

# Create draft via HTTP API (requires user_id)
curl -X POST "http://localhost:8000/drafts/create-markup" -H "Content-Type: application/json" -d "{\"user_id\": \"your_user_id\", \"title\": \"Test\", \"markup_content\": \"Title:: Hello | Text:: **Bold** content\"}"

# List drafts for specific account
curl "http://localhost:8000/drafts?user_id=your_user_id"

# Publish draft (REQUIRES user_id and draft_id in body!)
curl -X POST "http://localhost:8000/drafts/123456/publish" -H "Content-Type: application/json" -d "{\"user_id\": \"your_user_id\", \"draft_id\": 123456, \"send_email\": false, \"audience\": \"everyone\"}"

# Update environment for specific account (requires user_id)
curl -X POST "http://localhost:8000/webhook/update-environment" -H "Content-Type: application/json" -d "{\"user_id\": \"your_user_id\", \"sid\": \"new_sid_value\", \"substack_sid\": \"new_substack_sid\", \"substack_lli\": \"new_substack_lli\"}"

# Update only specific fields for account
curl -X POST "http://localhost:8000/webhook/update-environment" -H "Content-Type: application/json" -d "{\"user_id\": \"your_user_id\", \"sid\": \"new_value\"}"

# Create new account via webhook (user_id required)
curl -X POST "http://localhost:8000/webhook/update-environment" -H "Content-Type: application/json" -d "{\"user_id\": \"newuser\", \"publication_url\": \"https://newaccount.substack.com\", \"sid\": \"new_cookies\"}"
```

**IMPORTANT:** 
- **All API endpoints now require `user_id` parameter** to specify which account to use
- Publish endpoint requires `draft_id` AND `user_id` in the JSON body plus draft_id in URL
- Environment webhook requires `user_id` to identify target account
- Webhook automatically creates new account files for unknown user_ids
- Environment webhook should be protected by Cloudflare Access rules in production
- All webhook parameters are optional except `user_id`

## Markup Syntax Quick Reference

**Basic Format:** `Type:: Content | Type:: Content | Type:: Content`

**Content Types:**
- `Title::` Main heading | `Subtitle::` Secondary heading
- `Text::` Paragraph with **bold**, *italic*, [links](url)  
- `Quote::` Block quote | `PullQuote::` Emphasized quote
- `List::` • Item 1 • Item 2 | `NumberList::` 1. Item 1 1. Item 2
- `Code::` language | code here | `Rule::` (horizontal line)
- `Subscribe::` Button text | `Button::` Text -> url

**Example:** `Title:: My Post | Text:: Welcome with **bold** text | Subscribe:: Join Now`

## Key Implementation Notes

### Draft Creation Success Factors
1. **Use unpublished drafts as reference** - published drafts cause API errors
2. **Copy complete structure** - including bylines, publication settings
3. **Set required fields** - `should_send_email`, `subscriber_set_id`, etc.
4. **Fix byline IDs** - set `id = user_id` for draft bylines
5. **CRITICAL**: Filter empty text elements - empty text nodes with formatting marks break Substack's content parser
6. **Markup parsing** - proper regex handling for inline formatting without creating empty elements

### Publishing Workflow
1. **Interactive selection** - user chooses from available unpublished drafts
2. **Options configuration** - email sending, audience (everyone/paid)
3. **Immediate publishing** - uses `/api/v1/drafts/{id}/publish` endpoint
4. **Result confirmation** - shows post URL and success status

### Scheduling Limitations
- **New drafts:** Cannot be scheduled directly via API
- **Existing scheduled drafts:** Can be updated using discovered 5-step workflow
- **Workaround needed:** Use external scheduling systems + publish API

## Workaround Solutions

### For Scheduling New Drafts
1. **N8N + External Timer** - Use external scheduler to trigger publish API
2. **Manual pre-scheduling** - Create one schedule in web UI, then use API to update
3. **Hybrid approach** - External cron jobs + working publish endpoint

### Production Recommendations

### Environment Management & Security
- **Cookie Expiration**: Substack authentication cookies expire regularly
- **Webhook Solution**: Use `/webhook/update-environment` endpoint to update any .env values
- **Flexible Updates**: All parameters optional - update only what you need
- **Cloudflare Protection**: Protect webhook with Cloudflare Access rules
- **Authorized Sources**: Allow only trusted servers to send environment updates
- **Automatic Updates**: Set up monitoring to detect expired cookies and auto-refresh

### API Server Deployment
- **HTTP API**: Use `api_server.py` for production integrations
- **Environment Variables**: Set credentials via environment instead of `.env` file
- **Authentication**: Add API key authentication for production
- **Rate Limiting**: Implement rate limits for API endpoints
- **HTTPS**: Use reverse proxy (nginx) with SSL certificates
- **Process Management**: Use systemd, Docker, or PM2 for process management

### Command Line Usage
- Use working draft creation and publishing APIs
- Implement external scheduling layer for timing control
- Combine with workflow automation tools (N8N, Zapier, etc.)

## Error Handling Strategy
All scripts include comprehensive error handling:
- Input validation for user prompts and API requests
- API response checking with detailed error messages  
- Fallback options when operations fail
- Clear success/failure reporting with URLs
- **CRITICAL FIX**: Empty text elements with formatting marks filtered out (prevents Substack parser errors)

## Testing Approach
### Interactive Testing
- **API**: Interactive documentation at `http://localhost:8000/docs`
- **Command Line**: Interactive testing scripts guide users through workflows
- **Markup Validation**: API validates markup syntax before creating drafts

### Integration Testing  
- Use test endpoints for validation
- Comprehensive test draft creation with all content types
- Real-time API testing via Swagger UI