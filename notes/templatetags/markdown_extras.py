import bleach
import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# Conservative whitelist for Markdown-rendered HTML
ALLOWED_TAGS = [
    "p",
    "br",
    "blockquote",
    "pre",
    "code",
    "em",
    "strong",
    "ul",
    "ol",
    "li",
    "a",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "code": ["class"],
    "pre": ["class"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


@register.filter(name="markdownify")
def markdownify(value: str) -> str:
    """Render Markdown to sanitized HTML safe for display.

    - Convert Markdown to HTML with useful extensions (tables, fenced code, etc.)
    - Sanitize HTML output with Bleach to prevent XSS
    - Auto-link plain URLs
    """
    if not value:
        return ""

    html = md.markdown(
        value,
        extensions=[
            "extra",  # includes many common Markdown extensions
            "sane_lists",
            "tables",
            "fenced_code",
            "codehilite",  # adds classes for syntax highlighting
            "smarty",
        ],
        output_format="html5",
    )

    # Sanitize rendered HTML
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )

    # Linkify plain URLs safely
    cleaned = bleach.linkify(cleaned)

    return mark_safe(cleaned)
