#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wechat-publisher（yml_C4B 版）— Markdown / Word → 微信公众号 HTML

基于官方 starter kit 扩展，相比 starter 新增 6 项能力：
  1) 多主题配色      --theme {default,green,blue,dark}
  2) Callout 高亮框   （「> 📘 知识点」「> ⚠️ 注意」「> ✅ 实践」…）
  3) 自动目录          --toc
  4) 文章元数据        --title / --author / --date / --abstract
  5) 页脚版权          --footer
  6) 中文排版优化      --cjk（默认开启，中文与英文/数字自动加空格）

用法示例：
  python convert_to_wechat.py 文章.md 文章.html --theme green --toc \
      --title "标题" --author "虞梦琳" --date "2026-10-07" \
      --abstract "一句话摘要" --footer "© 2026 yml"

依赖：markdown / beautifulsoup4 / python-docx / lxml（首次运行自动安装）
"""

import sys
import os
import re
import argparse
from pathlib import Path


def install_dependencies():
    """缺失依赖时自动安装（与 starter 保持一致）。"""
    missing = []
    for mod, pkg in (("markdown", "markdown"), ("bs4", "beautifulsoup4"),
                     ("docx", "python-docx"), ("lxml", "lxml")):
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"安装缺失依赖: {', '.join(missing)} ...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               *missing, "--break-system-packages", "-q"])
        print("安装完成\n")


install_dependencies()

import markdown
from bs4 import BeautifulSoup
from docx import Document

# ---- 微信公众号允许的标签（内联样式优先）----
ALLOWED_TAGS = {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'span', 'img', 'a',
                'table', 'tr', 'th', 'td', 'br', 'blockquote'}
FORBIDDEN_TAGS = {'script', 'style', 'iframe', 'h1', 'div'}


# ---- 主题配色 ----
def _make_theme(heading, accent, link, code_bg="#f6f8fa", text="#333"):
    return {
        "h2": f"font-size: 22px; font-weight: bold; line-height: 1.6; color: {heading}; margin: 22px 0 10px 0;",
        "h3": f"font-size: 18px; font-weight: bold; line-height: 1.6; color: {heading}; margin: 16px 0 8px 0;",
        "p": f"font-size: 16px; line-height: 1.8; color: {text}; margin: 12px 0;",
        "li": f"font-size: 16px; line-height: 1.8; color: {text}; margin: 6px 0;",
        "a": f"color: {link}; text-decoration: underline;",
        "code_inline": f"background-color: #f5f5f5; color: {accent}; font-size: 14px; padding: 2px 5px; border-radius: 3px;",
        "code_block": f"background-color: {code_bg}; color: #24292e; font-size: 14px; line-height: 1.6; padding: 14px; margin: 12px 0;",
        "blockquote": f"background-color: #f9f9f9; color: #666; padding: 12px 16px; margin: 12px 0; border-left: 4px solid {accent};",
        "table": "border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;",
        "th": f"background-color: {code_bg}; color: #24292e; font-weight: bold; padding: 8px; text-align: left; border: 1px solid #ddd;",
        "td": f"padding: 8px; border: 1px solid #ddd; color: {text};",
    }


THEMES = {
    "default": _make_theme("#333", "#d73a49", "#0366d6"),
    "green":   _make_theme("#1e6f50", "#1a7f37", "#0969da", code_bg="#eef8f1"),
    "blue":    _make_theme("#1d4ed8", "#1d4ed8", "#0366d6", code_bg="#eef3fb"),
    "dark":    _make_theme("#e6e6e6", "#e6e6e6", "#58a6ff", code_bg="#161b22", text="#c9d1d9"),
}

# Callout 高亮框：标记 → (标签, 背景色, 左边框色, 文字色)
CALLOUTS = {
    "📘": ("知识点", "#eef3fb", "#1d4ed8", "#1e3a5f"),
    "💡": ("建议",   "#fff8e6", "#d97706", "#5c4a00"),
    "✅": ("实践",   "#eef8f1", "#1a7f37", "#14532d"),
    "⚠️": ("注意",   "#fff0f0", "#dc2626", "#7f1d1d"),
    "❌": ("避坑",   "#fdf2f2", "#b91c1c", "#7f1d1d"),
}

# ============================================================
# 中文排版优化（盘古之白：中文与英文/数字之间插入半角空格）
# ============================================================

_CJK_RE_1 = re.compile(r'([\u4e00-\u9fff])([A-Za-z0-9])')
_CJK_RE_2 = re.compile(r'([A-Za-z0-9])([\u4e00-\u9fff])')


def cjk_spacing(text):
    """在中文与英文字母/数字之间补半角空格（盘古之白规则）。"""
    text = _CJK_RE_1.sub(r'\1 \2', text)
    text = _CJK_RE_2.sub(r'\1 \2', text)
    return text


# ============================================================
# INPUT READERS
# ============================================================

def read_markdown(filepath):
    """Convert Markdown file to HTML string (with CJK spacing)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    html = markdown.markdown(content, extensions=[
        'extra',          # Tables, footnotes, etc.
        'fenced_code',    # ```code blocks```
        'nl2br',          # Newline → <br>
        'sane_lists',     # Better list handling
        'toc',            # [TOC] placeholder support
    ])
    return html


def read_docx(filepath):
    """Convert Word .docx to HTML string."""
    doc = Document(filepath)
    parts = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Map Word heading styles to HTML headings
        style_name = para.style.name if para.style else ''
        if style_name.startswith('Heading'):
            level = style_name.replace('Heading ', '')
            tag = 'h2' if level in ('1', '2') else 'h3'
            parts.append(f'<{tag}>{text}</{tag}>')
        else:
            # Process inline formatting (bold, italic)
            p_html = '<p>'
            for run in para.runs:
                t = run.text
                if not t:
                    continue
                if run.bold and run.italic:
                    p_html += f'<span style="font-weight:bold;font-style:italic;">{t}</span>'
                elif run.bold:
                    p_html += f'<span style="font-weight:bold;">{t}</span>'
                elif run.italic:
                    p_html += f'<span style="font-style:italic;">{t}</span>'
                else:
                    p_html += t
            p_html += '</p>'
            parts.append(p_html)

    return '\n'.join(parts)


# ============================================================
# HTML SANITIZER
# ============================================================

def sanitize(html, theme_styles):
    """
    Sanitize HTML for WeChat compatibility.

    Steps:
    1. Remove forbidden tags entirely (script, style, iframe)
    2. Convert h1 → h2, div → p
    3. Handle code blocks → styled paragraphs
    4. Handle callout boxes (📘/💡/✅/⚠️/❌) → styled paragraphs
    5. Handle blockquotes → styled paragraphs
    6. Convert strong/em → styled spans
    """
    soup = BeautifulSoup(html, 'lxml')

    # Remove forbidden tags
    for tag_name in ('script', 'style', 'iframe'):
        for el in soup.find_all(tag_name):
            el.decompose()

    # h1 → h2 (WeChat doesn't allow h1)
    for h1 in soup.find_all('h1'):
        h1.name = 'h2'

    # div → p
    for div in soup.find_all('div'):
        div.name = 'p'

    # <pre><code> → styled <p> (code block)
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        code_text = code.get_text() if code else pre.get_text()
        p = soup.new_tag('p')
        p.string = code_text
        p['style'] = theme_styles['code_block']
        pre.replace_with(p)

    # Inline <code> → styled <span>
    for code in soup.find_all('code'):
        span = soup.new_tag('span')
        span.string = code.get_text()
        span['style'] = theme_styles['code_inline']
        code.replace_with(span)

    # Callout boxes: <blockquote> whose text starts with a callout emoji
    for bq in soup.find_all('blockquote'):
        text = bq.get_text().strip()
        matched = None
        for emoji, (label, bg, border, color) in CALLOUTS.items():
            if text.startswith(emoji):
                matched = (emoji, label, bg, border, color)
                break
        if matched:
            emoji, label, bg, border, color = matched
            p = soup.new_tag('p')
            # Bold title line = emoji + label, body = rest of text
            title_span = soup.new_tag('span')
            title_span['style'] = 'font-weight: bold;'
            title_span.string = f'{emoji} {label}'
            p.append(title_span)
            # Append body text after a line break
            body_text = text[len(emoji):].strip()
            # Strip a leading label so「> 📘 知识点\n> 正文」doesn't duplicate "知识点"
            if body_text.startswith(label):
                body_text = body_text[len(label):].strip()
            if body_text:
                br = soup.new_tag('br')
                p.append(br)
                p.append(soup.new_string(body_text))
            p['style'] = (
                f'background-color: {bg}; color: {color}; padding: 12px 16px; '
                f'margin: 12px 0; border-left: 4px solid {border}; '
                f'line-height: 1.75;'
            )
            bq.replace_with(p)
        else:
            # Regular blockquote → styled <p>
            p = soup.new_tag('p')
            p.string = bq.get_text()
            p['style'] = theme_styles['blockquote']
            bq.replace_with(p)

    # <strong>/<b> → styled <span>
    for tag in soup.find_all(['strong', 'b']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-weight: bold;'
        tag.replace_with(span)

    # <em>/<i> → styled <span>
    for tag in soup.find_all(['em', 'i']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-style: italic;'
        tag.replace_with(span)

    return soup


def apply_styles(soup, theme_styles):
    """Apply default inline styles to all elements."""
    style_map = {
        'h2': theme_styles['h2'],
        'h3': theme_styles['h3'],
        'p': theme_styles['p'],
        'li': theme_styles['li'],
        'table': theme_styles['table'],
        'th': theme_styles['th'],
        'td': theme_styles['td'],
        'a': theme_styles['a'],
    }

    for tag_name, style in style_map.items():
        for el in soup.find_all(tag_name):
            existing = el.get('style', '')
            if existing:
                # Don't overwrite manually set styles (code blocks, callouts, etc.)
                continue
            el['style'] = style

    return soup


def clean_attributes(soup):
    """Remove class, id, and non-allowed CSS properties."""
    for tag in soup.find_all(True):
        # Remove class and id
        for attr in ('class', 'id'):
            if attr in tag.attrs:
                del tag.attrs[attr]

        # Unwrap tags not in allowed list (keep their content)
        if tag.name not in ALLOWED_TAGS and tag.name not in ('html', 'head', 'body', '[document]'):
            tag.unwrap()

    return soup


# ============================================================
# ENHANCED FEATURES: metadata, TOC, footer, CJK spacing
# ============================================================

def build_toc(soup):
    """Build a table of contents from h2/h3 headings as a styled block."""
    headings = soup.find_all(['h2', 'h3'])
    if not headings:
        return None

    toc = soup.new_tag('p')
    toc['style'] = (
        'background-color: #f8f9fa; padding: 14px 16px; margin: 16px 0; '
        'border-left: 4px solid #0366d6; color: #333; font-size: 15px; '
        'line-height: 1.9;'
    )
    # Title
    title_span = soup.new_tag('span')
    title_span['style'] = 'font-weight: bold; font-size: 16px; color: #0366d6;'
    title_span.string = '📑 目录'
    toc.append(title_span)
    toc.append(soup.new_string('\n'))

    for h in headings:
        level = h.name
        text = h.get_text().strip()
        indent = '  ' if level == 'h3' else ''
        toc.append(soup.new_string(f'\n{indent}· {text}'))

    return toc


def build_metadata(soup, meta):
    """Build article metadata block (author / date / abstract)."""
    if not meta or not any(meta.values()):
        return None

    p = soup.new_tag('p')
    p['style'] = (
        'background-color: #f0f6ff; padding: 12px 16px; margin: 16px 0; '
        'border-left: 4px solid #0366d6; color: #444; font-size: 14px; '
        'line-height: 1.7;'
    )
    parts = []
    if meta.get('author'):
        parts.append(f"✍️ 作者：{meta['author']}")
    if meta.get('date'):
        parts.append(f"📅 日期：{meta['date']}")
    if meta.get('abstract'):
        parts.append(f"📋 摘要：{meta['abstract']}")
    p.string = '\n'.join(parts)
    return p


def build_footer(soup, footer_text):
    """Build a footer / copyright notice block."""
    p = soup.new_tag('p')
    p['style'] = (
        'text-align: center; color: #999; font-size: 13px; '
        'margin: 24px 0 8px 0; padding-top: 12px; '
        'border-top: 1px solid #eee; line-height: 1.6;'
    )
    p.string = footer_text or '—— 本文由 wechat-publisher 技能生成 ——'
    return p


def apply_cjk_spacing(soup):
    """Walk text nodes and insert CJK-English/digit spacing (skips code)."""
    for el in soup.find_all(['p', 'li', 'td', 'th', 'span', 'h2', 'h3', 'a']):
        # Skip code blocks / inline code (already styled)
        style = el.get('style', '')
        if 'code' in style and ('background' in style or 'monospace' in style):
            continue
        for child in el.children:
            if isinstance(child, str) and child.strip():
                new_text = cjk_spacing(child)
                child.replace_with(new_text)
    return soup


# ============================================================
# MAIN CONVERTER
# ============================================================

def convert(input_path, output_path, theme='default', meta=None, toc=False,
            footer=None, cjk=True):
    """Main conversion pipeline: read → sanitize → style → clean → enhance → output."""
    path = Path(input_path)

    if not path.exists():
        print(f"❌ Error: File '{input_path}' not found.")
        return False

    ext = path.suffix.lower()
    theme_styles = THEMES.get(theme, THEMES['default'])

    # Step 1: Read input
    print(f"📖 Reading {path.name} ({ext})...")
    if ext == '.md':
        html = read_markdown(input_path)
    elif ext == '.docx':
        html = read_docx(input_path)
    elif ext in ('.html', '.htm'):
        with open(input_path, 'r', encoding='utf-8') as f:
            html = f.read()
    else:
        print(f"❌ Unsupported format: {ext}")
        print("   Supported: .md, .docx, .html")
        return False

    # Step 2: Sanitize
    print("🧹 Sanitizing HTML for WeChat...")
    soup = sanitize(html, theme_styles)

    # Step 3: Apply styles
    print(f"🎨 Applying WeChat styles (theme: {theme})...")
    soup = apply_styles(soup, theme_styles)

    # Step 4: Clean attributes
    print("✂️  Cleaning non-allowed attributes...")
    soup = clean_attributes(soup)

    # Step 5: Enhanced features (metadata, TOC, footer, CJK)
    body = soup.find('body') or soup
    prepend_nodes = []
    if toc:
        toc_node = build_toc(soup)
        if toc_node:
            print("📑 Generating table of contents...")
            prepend_nodes.append(toc_node)
    if meta and any(meta.values()):
        meta_node = build_metadata(soup, meta)
        if meta_node:
            print("📋 Adding article metadata...")
            prepend_nodes.append(meta_node)

    # Insert prepend nodes at top of body (metadata first, then TOC)
    for node in reversed(prepend_nodes):
        body.insert(0, node)

    # Footer at end of body
    footer_node = build_footer(soup, footer)
    body.append(footer_node)

    if cjk:
        print("🔤 Applying CJK typography spacing...")
        soup = apply_cjk_spacing(soup)

    # Step 6: Extract body content
    content = '\n'.join(str(child) for child in body.children if str(child).strip())

    # Wrap in minimal HTML shell for browser preview
    title = (meta or {}).get('title', 'WeChat Article Preview')
    output_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
</head>
<body style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
{content}
</body>
</html>"""

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ Done! {output_path} ({size_kb:.1f} KB)")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_path} in a browser to preview")
    print(f"   2. Ctrl+A → Ctrl+C (select all, copy)")
    print(f"   3. Go to mp.weixin.qq.com → create new article")
    print(f"   4. Ctrl+V (paste into editor)")
    print(f"   5. Upload images via WeChat media library if needed")
    print(f"   6. Preview on phone → publish!")

    return True


def main():
    import argparse
    ap = argparse.ArgumentParser(description='WeChat Publisher — Markdown/Word → 公众号 HTML')
    ap.add_argument('input', help='Input file (.md / .docx / .html)')
    ap.add_argument('output', help='Output HTML path')
    ap.add_argument('--theme', default='default', choices=list(THEMES),
                    help='Color theme (default/green/blue/dark)')
    ap.add_argument('--title', default=None, help='Article title')
    ap.add_argument('--author', default=None, help='Article author')
    ap.add_argument('--date', default=None, help='Publish date')
    ap.add_argument('--abstract', default=None, help='Article abstract')
    ap.add_argument('--toc', action='store_true', help='Auto-generate table of contents')
    ap.add_argument('--footer', default=None, help='Footer / copyright text')
    ap.add_argument('--no-cjk', action='store_true', help='Disable CJK spacing')
    args = ap.parse_args()

    meta = {'title': args.title, 'author': args.author,
            'date': args.date, 'abstract': args.abstract}
    success = convert(args.input, args.output, theme=args.theme, meta=meta,
                      toc=args.toc, footer=args.footer, cjk=not args.no_cjk)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
