# Substack API Client

A fully functional Python-based Substack API client that enables programmatic creation, management, and publishing of Substack posts with rich formatting support. Available as both **command-line tools** and **HTTP REST API**.

## Features ✅

### ✅ Working Functionality
- **Draft Creation**: Create drafts with rich formatting using simple markup syntax
- **Draft Publishing**: Interactive publishing with email/audience options
- **Rich Content**: All Substack content types supported (headings, lists, quotes, buttons, etc.)
- **User-Friendly Markup**: Write formatted content using simple syntax
- **Environment Management**: Easy credential setup and management
- **🆕 HTTP API**: REST API server for integration with any programming language
- **🆕 Web Interface**: Interactive API documentation and testing

### ❌ Known Limitations  
- **Scheduling**: Cannot create new schedules via API (can only update existing ones)
- **Media Upload**: Images/audio/video require separate upload process

## Quick Start

### 🚀 API Server (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials
python change_env.py

# Start API server
python api_server.py
```

**Server URL**: http://localhost:8000  
**Interactive Docs**: http://localhost:8000/docs

### 💻 Command Line Tools

```bash
# Install requirements
pip install requests python-dotenv

# Configure credentials  
python change_env.py
```

You'll need these credentials from your Substack account:
- **Publication URL**: Your Substack homepage (e.g., `https://yourname.substack.com`)
- **User ID**: Your Substack username
- **Authentication Cookies**: Extract from browser (see guide below)

### 2. Get Authentication Cookies
1. Login to your Substack account in browser
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies → https://substack.com  
4. Find and copy these cookie values:
   - `sid`
   - `substack.sid` 
   - `substack.lli`

### 3. Create Your First Draft

**API Method (Recommended):**
```bash
# Create draft via HTTP API
curl -X POST "http://localhost:8000/drafts/create-markup" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "markup_content": "Title:: Hello World | Text:: This is **bold** content | Subscribe:: Join Newsletter"
  }'
```

**Command Line Method:**
```bash
python draft_create.py
```

Choose from these options:
1. **Simple text draft** - Basic text content
2. **Markup draft** - Rich formatted content (reads from `sampleinput/2.txt`)
3. **Test draft** - Comprehensive example with all content types
4. **Rich formatting** - Basic formatting example

## Markup Syntax Guide

Create rich Substack content using simple markup:

### Basic Format
```
Title:: Your Main Heading | Text:: Your content with **bold** and *italic* | Subscribe:: Join Newsletter
```

### Content Types
- `Title::` - Main heading (H1)
- `Subtitle::` - Secondary heading (H2)  
- `H1:: - H6::` - Custom heading levels
- `Text::` - Paragraph with inline formatting
- `Quote::` - Block quote
- `PullQuote::` - Emphasized quote
- `List::` - Bullet list (• separated)
- `NumberList::` - Numbered list (1. 2. 3.)
- `Code::` - Code block (`language | code`)
- `Rule::` - Horizontal divider
- `Button::` - Custom button (`text -> url`)
- `Subscribe::` - Subscribe button
- `Share::` - Share button
- `Comment::` - Comment button
- `SubscribeWidget::` - Subscribe with description (`button >> description`)
- `LaTeX::` - Mathematical equations
- `Break::` - Empty paragraph/line break

### Inline Formatting
Within `Text::` blocks:
- `**bold**` - Bold text
- `*italic*` - Italic text  
- `~~strikethrough~~` - Strikethrough text
- `` `code` `` - Inline code
- `[link text](url)` - Links

### Example Markup
```
Title:: Market Analysis Report | Text:: Our analysis shows **strong growth** in tech stocks. Key findings: | List:: • Revenue up 25% • User growth at 40% • New product launches | Quote:: This represents the strongest quarter in company history | Subscribe:: Get Weekly Reports
```

## Publishing Drafts

**API Method:**
```bash
# List drafts
curl "http://localhost:8000/drafts"

# Publish specific draft
curl -X POST "http://localhost:8000/drafts/123456/publish" \
  -H "Content-Type: application/json" \
  -d '{"send_email": true, "audience": "everyone"}'
```

**Command Line Method:**
```bash
python draft_publish.py
```

- Lists all unpublished drafts with previews
- Choose draft and publishing options
- Publishes immediately with confirmation

## File Structure

```
substack-api/
├── api_server.py           # 🆕 HTTP REST API server
├── requirements.txt        # 🆕 API dependencies
├── API_GUIDE.md           # 🆕 Complete API documentation
├── draft_create.py         # Create drafts with markup support
├── draft_publish.py        # Publish existing drafts  
├── change_env.py          # Manage environment credentials
├── getposts.py            # Analyze all posts and drafts
├── sampleinput/2.txt      # Sample markup content
├── docs/                  # Documentation and guides
├── .env                   # Your credentials (create this)
└── README.md             # This file
```

## Usage Modes

### 🌐 HTTP API (Recommended)
Perfect for:
- Web applications
- Mobile app backends
- CI/CD pipelines  
- Third-party integrations
- Remote automation

### 💻 Command Line
Perfect for:
- Local automation
- Quick testing
- One-off posts
- Development workflow

## Troubleshooting

### Common Issues

**Authentication Errors**
- Refresh your browser cookies - they expire regularly
- Run `python change_env.py` to update credentials

**Draft Creation Fails**  
- Ensure you have at least one unpublished draft (create manually first)
- Check that your `.env` file has all required values

**Content Not Displaying**
- Fixed: Was caused by empty text elements in markup parser
- Current version filters out problematic empty elements

### Debug Tools

**Analyze existing posts:**
```bash
python getposts.py
```

**View markup examples:**
```bash  
python docs/markup_examples.py
```

## Advanced Usage

### API Integration (Recommended)
```python
import requests

# Create draft via API
response = requests.post("http://localhost:8000/drafts/create-markup", json={
    "title": "My Post",
    "markup_content": "Title:: Hello World | Text:: This is **bold** content",
    "subtitle": "Optional subtitle"
})

draft = response.json()
print(f"Created draft {draft['draft_id']}")

# Publish draft
requests.post(f"http://localhost:8000/drafts/{draft['draft_id']}/publish", json={
    "send_email": True,
    "audience": "everyone"
})
```

### Direct Function Import
```python
from draft_create import create_markup_draft

# Create draft from markup
draft = create_markup_draft(
    title="My Post",
    markup_content="Title:: Hello World | Text:: This is **bold** content",
    subtitle="Optional subtitle"
)
```

### Environment Variables
Required in `.env` file:
```
PUBLICATION_URL=https://yourname.substack.com
USER_ID=your_username
SID=cookie_value
SUBSTACK_SID=cookie_value  
SUBSTACK_LLI=cookie_value
```

## Contributing

The API client works by:
1. Using session-based authentication with browser cookies
2. Copying structure from existing unpublished drafts  
3. Converting markup syntax to Substack's JSON content format
4. Making authenticated requests to Substack's internal API endpoints

Key technical notes:
- Empty text elements break Substack's parser (now filtered out)
- Byline IDs must match user IDs for draft creation
- Content uses hierarchical JSON structure with `type`, `attrs`, `content`, `marks`

## Support

For issues or questions:
- Check the troubleshooting section above
- Review `docs/` folder for detailed technical guides  
- Ensure your authentication cookies are current

---

**Note**: This tool uses Substack's internal API endpoints. While functional, it may break if Substack changes their API structure.