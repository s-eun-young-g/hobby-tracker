"""Generated SVG placeholder covers for entries that have no artwork.

Games (and papers) have no per-entry image, so the gallery falls back to one of
these. A cover is drawn in whatever colour the caller passes (the active palette
accent for games, the hobby's own colour otherwise). To replace a placeholder
with real box art, drop a file under ``tally/web/static/covers/`` and it wins:

    static/covers/<theme>/<hobby>.png   palette-specific stock art (preferred)
    static/covers/<hobby>.png           one image used for every palette

Fonts are kept to generic ``sans-serif`` on purpose: an SVG loaded through an
<img>/background cannot pull in a web font, so we lean on what is installed.
"""

from __future__ import annotations

from .. import hobbies as H

# A short monogram per hobby. One glyph reads as an app icon; two still fit.
_MONO = {
    "quartiles": "Q", "crossword": "#", "set": "S", "anagrams": "A",
    "word_hunt": "W", "dialed_sound": "50", "paper": "P", "book": "B",
    "movie": "M", "dances": "D",
}

PAPER = "#fffdf8"
INK = "#15130f"
MUTED = "#6f6557"
FAINT = "#9a8f7d"


def _text_on(hex_color: str) -> str:
    """Pick ink or paper for text sitting on ``hex_color`` (by luminance)."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return INK
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else PAPER


def cover_svg(key: str, color: str | None = None) -> str:
    """Return an SVG document (2:3 poster) standing in for a missing cover."""
    h = H.get(key)
    color = color or (h.color if h else "#9fc7ec")
    fg = _text_on(color)
    label = (h.label if h else key.replace("_", " ")).upper()
    mono = _MONO.get(key, label[:1])
    mono_size = 64 if len(mono) == 1 else 42
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450" '
        f'width="300" height="450" role="img" aria-label="{label} placeholder cover">'
        '<defs><clipPath id="w">'
        '<rect x="12" y="12" width="276" height="426" rx="16"/></clipPath></defs>'
        f'<rect width="300" height="450" fill="{PAPER}"/>'
        '<g clip-path="url(#w)">'
        f'<rect x="12" y="12" width="276" height="426" fill="{PAPER}"/>'
        # title bar in the cover colour, with an outlined circle + heart
        f'<rect x="12" y="12" width="276" height="42" fill="{color}"/>'
        f'<circle cx="33" cy="33" r="6" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
        f'<g transform="translate(44 26.5) scale(0.44)" fill="{PAPER}" stroke="{INK}" '
        'stroke-width="4.5" stroke-linejoin="round">'
        '<path d="M23.6 0c-3.4 0-6.3 2.7-7.6 5.6C14.7 2.7 11.8 0 8.4 0 3.8 0 0 3.8 0 8.4'
        'c0 9.4 9.5 11.9 16 21.2 6.1-9.3 16-12.1 16-21.2C32 3.8 28.2 0 23.6 0z"/></g>'
        f'<text x="156" y="39" text-anchor="middle" font-family="sans-serif" '
        f'font-size="15" font-weight="700" letter-spacing="2" fill="{fg}">{label}</text>'
        # rounded "app icon" with the monogram
        f'<rect x="92" y="118" width="116" height="116" rx="26" fill="{color}" '
        f'stroke="{INK}" stroke-width="4"/>'
        f'<text x="150" y="196" text-anchor="middle" font-family="sans-serif" '
        f'font-size="{mono_size}" font-weight="700" fill="{fg}">{mono}</text>'
        # three dots motif
        f'<g fill="{color}">'
        '<circle cx="118" cy="298" r="7"/><circle cx="150" cy="298" r="7"/>'
        '<circle cx="182" cy="298" r="7"/></g>'
        f'<text x="150" y="372" text-anchor="middle" font-family="sans-serif" '
        f'font-size="13" letter-spacing="3" fill="{MUTED}">PLACEHOLDER</text>'
        f'<text x="150" y="402" text-anchor="middle" font-family="sans-serif" '
        f'font-size="12" letter-spacing="2" fill="{FAINT}">tally</text>'
        '</g>'
        f'<rect x="12" y="12" width="276" height="426" rx="16" fill="none" '
        f'stroke="{INK}" stroke-width="4"/>'
        '</svg>'
    )
