# Substack API Server Guide

HTTP API server that exposes Substack functionality via REST endpoints instead of command-line scripts.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Option 1: Use existing command
python change_env.py

# Option 2: Use API endpoint (after server starts)
curl -X PUT "http://localhost:8000/environment" \
  -H "Content-Type: application/json" \
  -d '{
    "publication_url": "https://yourname.substack.com",
    "user_id": "your_username",
    "sid": "cookie_value",
    "substack_sid": "cookie_value", 
    "substack_lli": "cookie_value"
  }'
```

### 3. Start API Server
```bash
python api_server.py
```

Server runs on: http://localhost:8000
Interactive docs: http://localhost:8000/docs

## API Endpoints

### 📝 Create Draft from Markup
```bash
POST /drafts/create-markup
Content-Type: application/json

{
  "title": "My Post Title",
  "markup_content": "Title:: Hello World | Text:: This is **bold** content | Subscribe:: Join Now",
  "subtitle": "Optional subtitle"
}
```

**Response:**
```json
{
  "success": true,
  "draft_id": 123456,
  "title": "My Post Title", 
  "subtitle": "Optional subtitle",
  "url": "https://yourname.substack.com/publish/post/123456",
  "message": "Draft created successfully with 3 content blocks"
}
```

### 🧪 Create Test Draft
```bash
POST /drafts/create-test
```

Creates comprehensive test draft with all content types (headings, lists, quotes, buttons, etc.)

### 📋 List Unpublished Drafts  
```bash
GET /drafts
```

**Response:**
```json
[
  {
    "id": 123456,
    "title": "My Post Title",
    "subtitle": "Optional subtitle",
    "content_preview": "This is bold content...",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### 🚀 Publish Draft
```bash
POST /drafts/{draft_id}/publish
Content-Type: application/json

{
  "send_email": true,
  "audience": "everyone"  // or "paid"
}
```

**Response:**
```json
{
  "success": true,
  "post_id": 123456,
  "post_url": "https://yourname.substack.com/p/my-post-title",
  "message": "Draft published successfully"
}
```

### 🔧 Update Environment
```bash
PUT /environment
Content-Type: application/json

{
  "publication_url": "https://yourname.substack.com",
  "user_id": "your_username",
  "sid": "new_cookie_value"
}
```

### 📖 Get Markup Syntax Guide
```bash
GET /markup-syntax
```

Returns complete syntax reference for markup formatting.

## Markup Syntax (API)

Same syntax as command-line version:

### Basic Format
```
Type:: Content | Type:: Content | Type:: Content
```

### Example API Request
```bash
curl -X POST "http://localhost:8000/drafts/create-markup" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Market Analysis", 
    "markup_content": "Title:: Gold Market Update | Text:: Analysis shows **strong performance** this quarter with [key trends](https://example.com) | Quote:: Gold remains the ultimate store of value | List:: • Central bank buying • Inflation hedging • Geopolitical tensions | Subscribe:: Get Market Updates"
  }'
```

## Integration Examples

### Python Client
```python
import requests

# Create draft
response = requests.post("http://localhost:8000/drafts/create-markup", json={
    "title": "My Post",
    "markup_content": "Title:: Hello | Text:: This is **bold** | Subscribe:: Join"
})

draft = response.json()
print(f"Created draft {draft['draft_id']}")

# Publish draft
requests.post(f"http://localhost:8000/drafts/{draft['draft_id']}/publish", json={
    "send_email": True,
    "audience": "everyone"
})
```

### JavaScript/Node.js
```javascript
// Create draft
const response = await fetch('http://localhost:8000/drafts/create-markup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'My Post',
    markup_content: 'Title:: Hello | Text:: This is **bold** | Subscribe:: Join'
  })
});

const draft = await response.json();
console.log(`Created draft ${draft.draft_id}`);
```

### cURL Examples
```bash
# Create draft
curl -X POST "http://localhost:8000/drafts/create-markup" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "markup_content": "Text:: Hello **world**"}'

# List drafts
curl "http://localhost:8000/drafts"

# Publish draft
curl -X POST "http://localhost:8000/drafts/123456/publish" \
  -H "Content-Type: application/json" \
  -d '{"send_email": true, "audience": "everyone"}'
```

## Error Handling

API returns standard HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid markup syntax)
- `500` - Internal server error (environment not configured, API failure)

Example error response:
```json
{
  "detail": "Invalid markup syntax: unexpected token at position 15"
}
```

## Development & Testing

### Interactive Documentation
Visit http://localhost:8000/docs for Swagger UI with:
- Interactive API testing
- Request/response schemas
- Example requests

### Health Check
```bash
curl http://localhost:8000/
```

Returns API info and available endpoints.

## Production Deployment

For production use:

1. **Environment Variables**: Set via environment instead of `.env` file
2. **Authentication**: Add API key authentication
3. **Rate Limiting**: Implement rate limits
4. **HTTPS**: Use reverse proxy (nginx) with SSL
5. **Process Management**: Use systemd or Docker

Example Docker deployment:
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "api_server.py"]
```

## Advantages over CLI

- ✅ **HTTP Integration**: Easy to call from any programming language
- ✅ **Web Interface**: Interactive documentation at `/docs`
- ✅ **JSON Responses**: Structured data instead of console output
- ✅ **Scalable**: Can handle multiple requests
- ✅ **Remote Access**: Can run on server, access remotely
- ✅ **No File Dependencies**: Markup passed directly in requests

Perfect for:
- Web applications
- Automation scripts
- CI/CD pipelines
- Third-party integrations
- Mobile app backends