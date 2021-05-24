"""Markdown function wrappers."""

import markdown


def safe_markdown(text):
    p = '<p>'
    np = '</p>'
    md = markdown.markdown(text)
    if md.startswith(p) and md.endswith(np):
        md = md[len(p): -len(np)]
        return md
