"""
Template utilities for placeholder images.

Provides a simple tag to generate a random placeholder image URL from picsum
with a few visual variations (plain, blur, blur with intensity, greyscale).
"""

from __future__ import annotations

import random
from django import template

register = template.Library()


@register.simple_tag
def random_placeholder_url(width: int = 300, height: int = 200, seed: int | str | None = None) -> str:
    """Return a random picsum placeholder URL.

    The function randomly picks one of these variants:
    - https://picsum.photos/{width}/{height}/
    - https://picsum.photos/{width}/{height}/?blur
    - https://picsum.photos/{width}/{height}/?blur={n} where 1 <= n <= 10
    - https://picsum.photos/{width}/{height}/?greyscale

    Args:
        width: target width in pixels
        height: target height in pixels

    Returns:
        A URL string to a picsum placeholder image.
    """
    base = f"https://picsum.photos/{int(width)}/{int(height)}"
    choice = random.choice(["plain", "blur", "blur_intensity", "greyscale"])
    if choice == "plain":
        url = base
    elif choice == "blur":
        url = f"{base}?blur"
    elif choice == "blur_intensity":
        url = f"{base}?blur={random.randint(1, 10)}"
    else:
        # Greyscale variant (note: picsum also supports 'grayscale')
        url = f"{base}?greyscale"

    # Append stable random query for cache-busting per index/seed
    if seed not in (None, "", 0, "0"):
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}random={seed}"
    return url


