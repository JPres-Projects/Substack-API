# Substack Rich Content Structure Guide

This guide documents all available content types for creating rich Substack posts based on analysis of draft 172549420.

## Quick Start: User-Friendly Markup

**NEW**: You can now create rich Substack content using simple markup syntax! Use `python draft_create.py` → Option 2.

### Example Markup:
```
Title:: The Future of AI | Text:: This article explores **artificial intelligence** and its *growing impact* on society. | Quote:: AI will transform every industry. | List:: • Key trends • Recent developments • Future predictions | Subscribe:: Get AI Updates
```

### Markup Syntax:
- `|` separates content blocks
- `::` separates content type from content  
- `**bold**`, `*italic*`, `[link](url)` for inline formatting
- `Title::`, `Text::`, `Quote::`, `List::`, `Subscribe::`, etc.

Run `python markup_examples.py` for complete syntax guide and examples.

### Available Markup Types:
- **Structure**: `Title::`, `Subtitle::`, `H1::`-`H6::`, `Rule::`, `Break::`
- **Text**: `Text::` (supports **bold**, *italic*, ~~strikethrough~~, `code`, [links](url))
- **Quotes**: `Quote::`, `PullQuote::`
- **Lists**: `List::` (• separated), `NumberList::` (1. 2. 3.)
- **Code**: `Code:: language | your code here`
- **Buttons**: `Subscribe::`, `Share::`, `Comment::`, `Button:: text -> url`
- **Widgets**: `SubscribeWidget:: button >> description`, `ShareWidget:: button >> description`
- **Advanced**: `LaTeX:: equation`, `Footnote:: [1] text`

---

## Technical Reference: JSON Structure

All Substack content follows this pattern:
```json
{
  "type": "doc",
  "content": [
    // Array of content blocks
  ]
}
```

## Content Types Overview

**31 different content types** identified:
- Basic text formatting (bold, italic, code, strikethrough, links)
- Headings (H1-H6)
- Lists (bullet and numbered)
- Media (images, audio, video)
- Interactive elements (buttons, subscription widgets)
- Advanced content (LaTeX, footnotes, quotes)

## Text Formatting

### Basic Text
```json
{
  "type": "text",
  "text": "Your text here"
}
```

### Bold Text
```json
{
  "type": "text", 
  "marks": [{"type": "strong"}],
  "text": "Bold text"
}
```

### Italic Text
```json
{
  "type": "text",
  "marks": [{"type": "em"}],
  "text": "Italic text"  
}
```

### Strikethrough Text
```json
{
  "type": "text",
  "marks": [{"type": "strikethrough"}],
  "text": "Crossed out text"
}
```

### Inline Code
```json
{
  "type": "text",
  "marks": [{"type": "code"}],
  "text": "inline code"
}
```

### Links
```json
{
  "type": "text",
  "marks": [{
    "type": "link",
    "attrs": {
      "href": "https://example.com",
      "target": "_blank",
      "rel": "noopener noreferrer nofollow",
      "class": null
    }
  }],
  "text": "Link text"
}
```

## Headings

### H1-H6 Headings
```json
{
  "type": "heading",
  "attrs": {"level": 1},  // 1-6 for H1-H6
  "content": [{
    "type": "text",
    "text": "Heading text"
  }]
}
```

## Paragraphs

### Regular Paragraph
```json
{
  "type": "paragraph",
  "content": [{
    "type": "text",
    "text": "Paragraph content"
  }]
}
```

### Empty Paragraph (line break)
```json
{
  "type": "paragraph"
}
```

## Lists

### Bullet List
```json
{
  "type": "bullet_list",
  "content": [{
    "type": "list_item",
    "content": [{
      "type": "paragraph",
      "content": [{
        "type": "text",
        "text": "List item text"
      }]
    }]
  }]
}
```

### Numbered List
```json
{
  "type": "ordered_list",
  "attrs": {"start": 1, "order": 1},
  "content": [{
    "type": "list_item", 
    "content": [{
      "type": "paragraph",
      "content": [{
        "type": "text",
        "text": "List item text"
      }]
    }]
  }]
}
```

## Quotes

### Block Quote
```json
{
  "type": "blockquote",
  "content": [{
    "type": "paragraph",
    "content": [{
      "type": "text",
      "text": "Quote text"
    }]
  }]
}
```

### Pull Quote (Emphasized Quote)
```json
{
  "type": "pullquote",
  "attrs": {"align": null, "color": null},
  "content": [{
    "type": "paragraph", 
    "content": [{
      "type": "text",
      "text": "Emphasized quote text"
    }]
  }]
}
```

## Code Blocks

```json
{
  "type": "code_block",
  "attrs": {"language": null},  // or "python", "javascript", etc.
  "content": [{
    "type": "text",
    "text": "code here"
  }]
}
```

## Images

### Basic Image
```json
{
  "type": "captionedImage",
  "content": [{
    "type": "image2",
    "attrs": {
      "src": "https://substack-post-media.s3.amazonaws.com/...",
      "height": 313,
      "width": 364,
      "alt": "Alt text",
      "type": "image/png"
      // ... other image properties
    }
  }]
}
```

### Image with Caption
```json
{
  "type": "captionedImage",
  "content": [
    {
      "type": "image2",
      "attrs": { /* image attributes */ }
    },
    {
      "type": "caption",
      "content": [{
        "type": "text",
        "text": "Caption text"
      }]
    }
  ]
}
```

## Media

### Audio
```json
{
  "type": "audio",
  "attrs": {
    "mediaUploadId": "uuid-here",
    "duration": 183.43,
    "isEditorNode": true
  }
}
```

### Video
```json
{
  "type": "video", 
  "attrs": {
    "mediaUploadId": "uuid-here",
    "duration": null
  }
}
```

## Interactive Elements

### Basic Button
```json
{
  "type": "button",
  "attrs": {
    "url": "https://example.com",
    "text": "Button Text",
    "action": null,
    "class": null
  }
}
```

### Subscription Button
```json
{
  "type": "button",
  "attrs": {
    "url": "%%checkout_url%%",
    "text": "Subscribe",
    "action": null,
    "class": null
  }
}
```

### Subscribe Widget (with description)
```json
{
  "type": "subscribeWidget",
  "attrs": {
    "url": "%%checkout_url%%",
    "text": "Subscribe",
    "language": "en"
  },
  "content": [{
    "type": "ctaCaption",
    "content": [{
      "type": "text",
      "text": "Description text"
    }]
  }]
}
```

### Share Button with Caption
```json
{
  "type": "captionedShareButton", 
  "attrs": {
    "url": "%%share_url%%",
    "text": "Share"
  },
  "content": [{
    "type": "ctaCaption",
    "content": [{
      "type": "text",
      "text": "Share description"
    }]
  }]
}
```

### Direct Message Button
```json
{
  "type": "directMessage",
  "attrs": {
    "userId": 370411012,
    "userName": "Author Name",
    "isEditorNode": true,
    "isEditor": true
  }
}
```

## Advanced Content

### Horizontal Rule
```json
{
  "type": "horizontal_rule"
}
```

### LaTeX Block
```json
{
  "type": "latex_block",
  "attrs": {
    "persistentExpression": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}\n",
    "id": "UNIQUE_ID"
  }
}
```

### Footnotes

#### Footnote Reference
```json
{
  "type": "footnoteAnchor",
  "attrs": {"number": 1}
}
```

#### Footnote Definition
```json
{
  "type": "footnote",
  "attrs": {"number": 1},
  "content": [{
    "type": "paragraph",
    "content": [{
      "type": "text", 
      "text": "Footnote content"
    }]
  }]
}
```

## Magic URLs

Substack provides special URLs that are dynamically replaced:

- `%%checkout_url%%` - Subscribe/payment URL
- `%%share_url%%` - Share post URL  
- `%%half_magic_comments_url%%` - Comments URL

## Usage Notes

1. **Media Files**: Audio/video require `mediaUploadId` from file uploads
2. **Images**: Must be uploaded to Substack's CDN first
3. **User-specific Data**: `userId` and `userName` should match your account
4. **Footnote Numbers**: Must be sequential and match between anchor and definition
5. **LaTeX**: Requires unique `id` field for each block
6. **Lists**: Can be nested by adding more `list_item` elements
7. **Text Marks**: Can be combined (e.g., bold + italic)

## Content Creation Tips

- Start with basic `doc` structure containing `content` array
- Build paragraphs with `text` elements inside
- Use `marks` array for text formatting
- Combine elements to create rich layouts
- Test complex structures in small chunks first
- Images and media require separate upload process

This structure enables creation of fully-featured Substack posts with all formatting and interactive elements available in the web editor.