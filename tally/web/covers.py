"""Generated SVG placeholder covers for entries that have no artwork.

Games get a bare-bones geometric motif (a stripped-down nod to the real game);
everything else falls back to a monogram. Covers share one visual language: ink
outlines, accent fills, a uniform stroke weight, on the cream window. To replace
a cover with real art, drop a file at ``tally/web/static/covers/<hobby>.png``.

Fonts are kept to generic ``sans-serif`` on purpose: an SVG loaded through an
<img>/background cannot pull in a web font, so we lean on what is installed.
"""

from __future__ import annotations

from .. import hobbies as H

PAPER = "#fffdf8"
INK = "#15130f"
MUTED = "#6f6557"
FAINT = "#9a8f7d"
STROKE = 5

# Monogram for hobbies without a geometric motif (book, movie, paper, dance...).
_MONO = {"paper": "P", "book": "B", "movie": "M", "dances": "D"}


def _text_on(hex_color: str) -> str:
    """Pick ink or paper for text sitting on ``hex_color`` (by luminance)."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return INK
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else PAPER


def _rect(x, y, w, h, fill, rx=0):
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{r} '
            f'fill="{fill}" stroke="{INK}" stroke-width="{STROKE}"/>')


# -- geometric motifs (one per game) -----------------------------------------
def _m_crossword(c: str) -> str:
    x0, y0, cell = 75, 160, 30
    filled = {(0, 1), (1, 3), (2, 0), (2, 4), (3, 1), (4, 3)}
    out = []
    for r in range(5):
        for col in range(5):
            fill = c if (r, col) in filled else PAPER
            out.append(_rect(x0 + col * cell, y0 + r * cell, cell, cell, fill))
    return "".join(out)


def _m_quartiles(c: str) -> str:
    cols, rows, tw, th, gx, gy = 3, 4, 46, 28, 10, 10
    x0 = 150 - (cols * tw + (cols - 1) * gx) / 2
    y0 = 235 - (rows * th + (rows - 1) * gy) / 2
    out = []
    for r in range(rows):
        for col in range(cols):
            out.append(_rect(x0 + col * (tw + gx), y0 + r * (th + gy), tw, th, c, rx=7))
    return "".join(out)


def _m_anagrams(c: str) -> str:
    size, gap, n = 32, 10, 4
    x0 = 150 - (n * size + (n - 1) * gap) / 2
    rot = [-8, 7, -6, 8]
    dy = [6, -5, 5, -6]
    out = []
    for i in range(n):
        tx = x0 + i * (size + gap)
        ty = 235 - size / 2 + dy[i]
        cxr, cyr = tx + size / 2, ty + size / 2
        out.append(f'<g transform="rotate({rot[i]} {cxr:.1f} {cyr:.1f})">'
                   + _rect(tx, ty, size, size, c, rx=6) + '</g>')
    return "".join(out)


def _m_word_hunt(c: str) -> str:
    x0, y0, cell, gap = 70, 155, 34, 8
    path = [(0, 1), (1, 0), (2, 1), (1, 2), (2, 3), (3, 2)]

    def center(r, col):
        return (x0 + col * (cell + gap) + cell / 2, y0 + r * (cell + gap) + cell / 2)

    out = []
    for r in range(4):
        for col in range(4):
            fill = c if (r, col) in path else PAPER
            out.append(_rect(x0 + col * (cell + gap), y0 + r * (cell + gap), cell, cell, fill, rx=5))
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (center(r, col) for r, col in path))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" '
               f'stroke-width="{STROKE + 1}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


def _m_set(c: str) -> str:
    top, bot = 165, 305
    common = f'fill="{c}" stroke="{INK}" stroke-width="{STROKE}" stroke-linejoin="round"'
    diamond = f'<polygon points="100,{top} 122,235 100,{bot} 78,235" {common}/>'
    capsule = f'<rect x="130" y="{top}" width="40" height="{bot - top}" rx="20" {common}/>'
    # a gentle S-ribbon (offset cubic-bezier edges) reading as the SET squiggle
    squiggle = ('<path d="M 213 165 C 227 193 227 207 213 235 C 199 263 199 277 213 305 '
                'L 187 305 C 173 277 173 263 187 235 C 201 207 201 193 187 165 Z" '
                f'{common}/>')
    return diamond + capsule + squiggle


def _m_dialed(c: str) -> str:
    bw, gap, n, base = 14, 10, 7, 305
    x0 = 150 - (n * bw + (n - 1) * gap) / 2
    heights = [46, 86, 60, 116, 74, 98, 54]
    out = [f'<line x1="{x0 - 4:.1f}" y1="{base}" x2="{x0 + n * bw + (n - 1) * gap + 4:.1f}" '
           f'y2="{base}" stroke="{INK}" stroke-width="{STROKE}" stroke-linecap="round"/>']
    for i in range(n):
        out.append(_rect(x0 + i * (bw + gap), base - heights[i], bw, heights[i], c, rx=3))
    return "".join(out)


_MOTIF = {
    "crossword": _m_crossword, "quartiles": _m_quartiles, "anagrams": _m_anagrams,
    "word_hunt": _m_word_hunt, "set": _m_set, "dialed_sound": _m_dialed,
}


def _monogram_body(key: str, color: str, fg: str) -> str:
    label = (H.get(key).label if H.get(key) else key).upper()
    mono = _MONO.get(key, label[:1])
    size = 64 if len(mono) == 1 else 42
    return (
        f'<rect x="92" y="150" width="116" height="116" rx="26" fill="{color}" '
        f'stroke="{INK}" stroke-width="4"/>'
        f'<text x="150" y="228" text-anchor="middle" font-family="sans-serif" '
        f'font-size="{size}" font-weight="700" fill="{fg}">{mono}</text>'
        f'<text x="150" y="330" text-anchor="middle" font-family="sans-serif" '
        f'font-size="12" letter-spacing="2" fill="{FAINT}">tally</text>'
    )


def cover_svg(key: str, color: str | None = None) -> str:
    """Return an SVG document (2:3 poster) standing in for a missing cover."""
    h = H.get(key)
    color = color or (h.color if h else "#c7bca3")
    fg = _text_on(color)
    label = (h.label if h else key.replace("_", " ")).upper()
    body = _MOTIF[key](color) if key in _MOTIF else _monogram_body(key, color, fg)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450" '
        f'width="300" height="450" role="img" aria-label="{label} cover">'
        '<defs><clipPath id="w">'
        '<rect x="12" y="12" width="276" height="426" rx="16"/></clipPath></defs>'
        f'<rect width="300" height="450" fill="{PAPER}"/>'
        '<g clip-path="url(#w)">'
        f'<rect x="12" y="12" width="276" height="426" fill="{PAPER}"/>'
        # title bar with an outlined circle + heart
        f'<rect x="12" y="12" width="276" height="42" fill="{color}"/>'
        f'<circle cx="33" cy="33" r="6" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
        f'<g transform="translate(44 26.5) scale(0.44)" fill="{PAPER}" stroke="{INK}" '
        'stroke-width="4.5" stroke-linejoin="round">'
        '<path d="M23.6 0c-3.4 0-6.3 2.7-7.6 5.6C14.7 2.7 11.8 0 8.4 0 3.8 0 0 3.8 0 8.4'
        'c0 9.4 9.5 11.9 16 21.2 6.1-9.3 16-12.1 16-21.2C32 3.8 28.2 0 23.6 0z"/></g>'
        f'<text x="156" y="39" text-anchor="middle" font-family="sans-serif" '
        f'font-size="15" font-weight="700" letter-spacing="2" fill="{fg}">{label}</text>'
        f'{body}'
        '</g>'
        f'<rect x="12" y="12" width="276" height="426" rx="16" fill="none" '
        f'stroke="{INK}" stroke-width="4"/>'
        '</svg>'
    )
