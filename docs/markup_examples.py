#!/usr/bin/env python3
"""
Examples of Substack markup syntax for easy reference
"""

def show_markup_examples():
    """Display comprehensive markup examples"""
    
    print("=== SUBSTACK MARKUP SYNTAX EXAMPLES ===\n")
    
    print("Basic Example:")
    example1 = """Title:: The Future of AI | Text:: This article explores **artificial intelligence** and its *growing impact* on society. We'll examine key trends and [recent developments](https://example.com). | Quote:: AI will transform every industry in the next decade. | Subscribe:: Get AI Updates"""
    print(f'"{example1}"\n')
    
    print("Complex Example with Multiple Elements:")
    example2 = """H1:: Market Analysis Report | H2:: Q4 Results | Text:: Our analysis shows **strong growth** in tech stocks. Key findings include: | List:: • Revenue up 25% • User growth at 40% • New product launches successful | Code:: python | def analyze_growth(data): return data.growth_rate * 100 | Quote:: This represents the strongest quarter in company history. | Rule:: | H2:: Investment Recommendations | NumberList:: 1. Increase tech allocation 1. Diversify into emerging markets 1. Monitor regulatory changes | SubscribeWidget:: Get Market Reports >> Stay informed with weekly market analysis and investment insights | ShareWidget:: Share Analysis >> Help others make informed investment decisions"""
    print(f'"{example2}"\n')
    
    print("=== SYNTAX REFERENCE ===\n")
    
    syntax_guide = [
        ("Title::", "Creates H1 heading", "Title:: My Blog Post"),
        ("Subtitle::", "Creates H2 heading", "Subtitle:: Weekly Update"),
        ("H1:: - H6::", "Creates headings level 1-6", "H3:: Section Header"),
        ("Text::", "Regular paragraph with formatting", "Text:: This is **bold** and *italic*"),
        ("Quote::", "Block quote", "Quote:: Wisdom is knowing what to do next"),
        ("PullQuote::", "Emphasized quote", "PullQuote:: Featured insight here"),
        ("List::", "Bullet list (use bullet separator)", "List:: • First • Second • Third"),
        ("NumberList::", "Numbered list", "NumberList:: 1. First 1. Second 1. Third"),
        ("Code::", "Code block (language | code)", "Code:: python | print('hello')"),
        ("Rule::", "Horizontal divider", "Rule::"),
        ("Button::", "Custom button (text -> url)", "Button:: Visit Site -> https://example.com"),
        ("Subscribe::", "Subscribe button", "Subscribe:: Join Newsletter"),
        ("Share::", "Share button", "Share:: Share This Post"),
        ("Comment::", "Comment button", "Comment:: Leave Feedback"),
        ("SubscribeWidget::", "Subscribe with description", "Subscribe:: Join >> Get weekly updates"),
        ("ShareWidget::", "Share with description", "Share:: Share >> Tell others about this"),
        ("LaTeX::", "Math equation", "LaTeX:: E = mc^2"),
        ("Footnote::", "Footnote definition", "Footnote:: [1] Source information"),
        ("Break::", "Empty paragraph/line break", "Break::"),
    ]
    
    print("Available Content Types:")
    for syntax, description, example in syntax_guide:
        print(f"  {syntax:<20} {description:<30} Example: {example}")
    
    print("\n=== INLINE FORMATTING ===")
    inline_guide = [
        ("**text**", "Bold text"),
        ("*text*", "Italic text"),
        ("~~text~~", "Strikethrough text"),
        ("`code`", "Inline code"),
        ("[text](url)", "Link"),
    ]
    
    print("Within Text:: blocks, use:")
    for markup, description in inline_guide:
        print(f"  {markup:<15} {description}")
    
    print("\n=== IMPORTANT NOTES ===")
    print("- Use | to separate different content blocks")
    print("- Use :: to separate content type from content")
    print("- Semicolons (;) in content are automatically converted to commas")
    print("- For lists, use * for bullets and 1. 2. 3. for numbers")
    print("- For code blocks: Code:: language | your code here")
    print("- For buttons with URLs: Button:: Text -> https://url")
    print("- For widgets with descriptions: Type:: Button >> Description")
    print("- Empty content types (like Rule::) create structural elements")
    
    print("\n=== MAGIC URLS ===")
    magic_urls = [
        ("Subscribe:: text", "Uses %%checkout_url%% (Substack subscribe)"),
        ("Share:: text", "Uses %%share_url%% (Share this post)"),
        ("Comment:: text", "Uses %%half_magic_comments_url%% (Comments)"),
    ]
    
    print("Special buttons automatically use Substack magic URLs:")
    for button, url in magic_urls:
        print(f"  {button:<20} -> {url}")

if __name__ == "__main__":
    show_markup_examples()
    
    print("\n=== TEST YOUR MARKUP ===")
    print("Try this example in the draft creator (option 2):")
    
    test_markup = """Title:: Test Post | Text:: Welcome to my **first** markup post! This shows *how easy* it is to create [rich content](https://substack.com). | Rule:: | Quote:: Markup makes formatting simple and intuitive. | List:: • Easy to write • Easy to read • Easy to maintain | Subscribe:: Join My Newsletter"""
    
    print(f'"{test_markup}"')
    print("\nRun: python draft_create.py → Choose option 2 → Paste the above markup")