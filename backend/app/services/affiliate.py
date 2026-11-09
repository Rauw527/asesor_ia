"""Deterministic affiliate link construction.

A language model must never be the source of a URL: it invents domains and dead
product pages. The model only proposes ``name``/``brand``/``reason``; the link is
built here from a configured search template plus the tracking tag.
"""

from __future__ import annotations

from urllib.parse import quote_plus

from app.core.config import Settings


def build_affiliate_link(config: Settings, *parts: str | None) -> str:
    query = " ".join(part.strip() for part in parts if part and part.strip())
    if not query:
        query = "skincare routine"
    url = config.affiliate_search_template.format(query=quote_plus(query))

    tag = config.affiliate_tag.strip()
    if tag:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}tag={quote_plus(tag)}"
    return url
