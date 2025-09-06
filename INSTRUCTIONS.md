# Quick Instructions - Multi-Account Support

## Start Server
```cmd
python api_server.py
```

## List All Accounts
```cmd
curl "http://localhost:8000/accounts"
```

## Create Test Post with ALL Elements (requires user_id)
```cmd
curl -X POST "http://localhost:8000/drafts/create-markup" -H "Content-Type: application/json" -d "{\"user_id\": \"your_user_id\", \"title\": \"Complete Test\", \"markup_content\": \"Title:: Main Heading | Subtitle:: Secondary Heading | H1:: Custom H1 | H2:: Custom H2 | H3:: Custom H3 | H4:: Custom H4 | H5:: Custom H5 | H6:: Custom H6 | Text:: Regular paragraph with **bold**, *italic*, ~~strikethrough~~, `inline code`, and [link](https://example.com) | Quote:: This is a block quote | PullQuote:: This is an emphasized pull quote | List:: • First item • Second item • Third item | NumberList:: 1. First numbered 1. Second numbered 1. Third numbered | Code:: python | def hello(): print('Hello World') | Rule:: | Button:: Click Here -> https://example.com | Subscribe:: Join Newsletter | Share:: Share This | Comment:: Leave Comment | SubscribeWidget:: Get Updates >> Subscribe for weekly insights | LaTeX:: E = mc^2 | Break::\"}"
```

## List Drafts for Account
```cmd
curl "http://localhost:8000/drafts?user_id=your_user_id"
```

## Publish Draft
```cmd
curl -X POST "http://localhost:8000/drafts/DRAFT_ID/publish" -H "Content-Type: application/json" -d "{\"user_id\": \"your_user_id\", \"draft_id\": DRAFT_ID, \"send_email\": false, \"audience\": \"everyone\"}"
```

## Update Environment for Specific Account
```cmd
curl -X POST "http://localhost:8000/webhook/update-environment" -H "Content-Type: application/json" -d "{\"user_id\": \"your_user_id\", \"publication_url\": \"https://yourpub.substack.com\", \"sid\": \"cookie_value\", \"substack_sid\": \"cookie_value\", \"substack_lli\": \"cookie_value\"}"
```

## Account Structure
- Environment files stored in `env/` directory
- Named as `.account1.env`, `.account2.env`, etc.
- Each account identified by `user_id` field
- All API calls require `user_id` parameter

**Note:** Use CMD, not PowerShell. Write commands in Notepad first, then copy/paste to CMD.