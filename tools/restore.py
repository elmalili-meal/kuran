#!/usr/bin/env python3
"""
Rebuild the browsable site in site/ from the raw snapshots in archive_original/.

The only changes made to each archived page are:
  1. removal of the Wayback Machine's injected <script>/<link>/comment blocks
  2. rewriting absolute wayback asset URLs back to the site's own relative paths
  3. re-encoding the bytes from windows-1254 to UTF-8 (+ matching <meta charset>)
  4. removal of the three graphical header tables (text-only restoration, by request)
  5. a small source/provenance line added bottom-right of every page

Markup, attributes, whitespace and the Turkish text itself are left untouched.
"""
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "archive_original"
# The restored pages live at the repository root so GitHub Pages can serve them
# straight from the main branch with no build step and no /docs indirection.
DST = ROOT

# Only these are generated output; everything else at the root is hand-written
# and must survive a rebuild.
GENERATED = ["index.html", "m_elmalili_index.htm", "melmalili",
             "sitemap.xml", "robots.txt"]

# Bottom-right provenance link. Points at the README, which carries the full
# story: the archived source, what was changed, and the copyright position.
# Uses the page's own font stack, so it introduces no styling of its own.
README_URL = "https://github.com/elmalili-meal/kuran/blob/main/README.md"

FOOTER = (
    '\n<table width="95%" border="0" cellspacing="0" cellpadding="0" align="center">\n'
    '  <tr>\n'
    '    <td align="right"><font face="Verdana, Arial, Helvetica, sans-serif" '
    f'size="1" color="#FFFFFF"><a href="{README_URL}">Kaynak</a></font></td>\n'
    '  </tr>\n'
    '</table>\n\n'
)

# Every <script> in these files is either Wayback's own injection or the
# orphaned "tavsiye" (tell-a-friend) form validators left behind by the original
# HTTrack mirror — no <form> survives on any page for them to act on.
WM_HEAD = re.compile(
    r'<script\b.*?</script>'
    r'|<link[^>]*web-static\.archive\.org[^>]*/?>'
    r'|<!--\s*End Wayback Rewrite JS Include\s*-->',
    re.S | re.I)
# trailing "FILE ARCHIVED ON ..." / "playback timings" comments
WM_TAIL = re.compile(r'<!--\s*\n?\s*(?:FILE ARCHIVED ON|playback timings).*?-->', re.S | re.I)
# /web/20240919080311im_/http://www.enfal.de/  ->  (relative)
WM_URL = re.compile(r'(?:https?://web\.archive\.org)?/web/\d{14}[a-z_]*/https?://(?:www\.)?enfal\.de/')
META_CHARSET = re.compile(
    r'<meta http-equiv="Content-Type" content="text/html; charset=[^"]*">\s*', re.I)

# The archived pages carry a bloated keyword-stuffed pair of meta tags (a relic
# of early-2000s SEO). Replaced with the concise versions requested.
META_DESCRIPTION = re.compile(r'<meta name="description" content="[^"]*">', re.I)
META_KEYWORDS = re.compile(r'<meta name="keywords" content="[^"]*">', re.I)

NEW_DESCRIPTION = ('<meta name="description" content="Elmalili M.hamdi '
                   'Yazir\'in Meali, konu indeksi">')
NEW_KEYWORDS = ('<meta name="keywords" content="Turkce,Kurani Kerim, elmalili, '
                'islamiyet, musluman">')

# --- search engine indexing -------------------------------------------------
# Public address the site is served from. Change this if the site moves; the
# canonical tags, sitemap.xml and robots.txt are all derived from it.
BASE_URL = "https://elmalili-meal.github.io/kuran/"
RESTORED_DATE = "2026-08-14"

HTML_OPEN = re.compile(r'<html\b[^>]*>', re.I)

# The index page carried a visible "kaynak: kuranikerim.com" credit line at the
# bottom right. Removed by request: that site is no longer reachable, so the
# credit points nowhere. The origin is still recorded in the README's provenance
# section and in the HTTrack comment left in every page's source.
OLD_CREDIT = re.compile(
    r'\s*<p align="right"><font color="#FFFFFF">kaynak: kuranikerim\.com</font></p>',
    re.I)


def strip_header_graphics(html: str) -> str:
    """Drop the three tables that only exist to carry the banner images:
    the ustb.gif strip, the white band of four JPEGs, and the altb.gif strip.
    They sit consecutively right after <body>, so we cut one contiguous span."""
    body = re.search(r'<body[^>]*>', html, re.I)
    alt = html.find("altb.gif")
    if not body or alt == -1:
        return html
    end = html.find("</table>", alt)
    if end == -1:
        return html
    return html[:body.end()] + "\n" + html[end + len("</table>"):].lstrip("\n")


def add_footer(html: str) -> str:
    # NB: never index via html.lower() here — Turkish "İ".lower() is two
    # codepoints, so offsets taken from the lowercased copy do not line up.
    matches = list(re.finditer(r'</body>', html, re.I))
    if not matches:
        return html
    i = matches[-1].start()
    return html[:i] + FOOTER + html[i:]


def add_seo(html: str, canonical: str, description: str) -> str:
    """Declare the page language and its canonical address.

    Both are invisible to the reader: nothing here changes a single pixel of the
    original design. The canonical tag matters because index.html and
    m_elmalili_index.htm serve identical content — without it search engines see
    duplicate pages and pick a winner themselves.
    """
    html = HTML_OPEN.sub('<html lang="tr">', html, count=1)
    link = f'<link rel="canonical" href="{canonical}">\n'
    # NB: match with a case-insensitive regex, never html.lower().find() —
    # Turkish "İ".lower() is two codepoints, so offsets taken from a lowercased
    # copy land mid-tag and split it.
    m = re.search(r'</head>', html, re.I)
    if m:
        html = html[:m.start()] + link + html[m.start():]
    if description:
        # quote=False keeps apostrophes readable; the attribute is double-quoted,
        # so only " needs escaping.
        safe = escape(description, quote=False).replace('"', "&quot;")
        tag = f'<meta name="description" content="{safe}">'
        if META_DESCRIPTION.search(html):
            html = META_DESCRIPTION.sub(tag, html, count=1)
        else:
            # the index page never carried a description tag of its own
            m = re.search(r'</head>', html, re.I)
            if m:
                html = html[:m.start()] + tag + "\n" + html[m.start():]
    return html


def convert(src: Path, depth: int, canonical: str = "", description: str = "") -> str:
    """depth = how many directories deep the page sits (0 = site root)."""
    html = src.read_bytes().decode("cp1254")
    html = WM_HEAD.sub("", html)
    html = WM_TAIL.sub("", html)
    html = WM_URL.sub("../" * depth, html)
    html = META_DESCRIPTION.sub(NEW_DESCRIPTION, html, count=1)
    html = META_KEYWORDS.sub(NEW_KEYWORDS, html, count=1)
    html = add_seo(html, canonical, description)
    html = OLD_CREDIT.sub("", html, count=1)
    html = strip_header_graphics(html)
    html = add_footer(html)
    # one UTF-8 declaration in place of the two legacy ones
    html = META_CHARSET.sub("", html, count=1)
    html = META_CHARSET.sub(
        '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n', html, count=1)
    # collapse the runs of blank lines left where scripts were removed
    html = re.sub(r'\n[ \t]*(?:\n[ \t]*){2,}', '\n\n', html)
    return html


def surah_labels(index_html: str) -> dict:
    """Map each surah file to its index label ("melmalili/fatiha.htm" -> "1-Fatiha").

    Taken from the index page's own link text, so the numbering and spelling are
    the original site's rather than anything invented here.
    """
    return {href: text.strip() for href, text in
            re.findall(r'href="(melmalili/[^"]+)"[^>]*>([^<]+)</a>', index_html)}


def write_sitemap(rel_paths) -> None:
    """List every publicly indexable page: the site root plus the 114 surahs.

    m_elmalili_index.htm is deliberately left out — it is byte-identical to the
    root URL and canonicalises to it, so listing it would advertise a duplicate.
    """
    urls = [BASE_URL] + [BASE_URL + rel for rel in rel_paths]
    body = "\n".join(
        f"  <url>\n    <loc>{escape(u)}</loc>\n"
        f"    <lastmod>{RESTORED_DATE}</lastmod>\n  </url>"
        for u in urls)
    (DST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{body}\n</urlset>\n', encoding="utf-8")


def write_robots() -> None:
    """Permit crawling of the site, but keep crawlers out of the working
    directories: archive_original/ holds raw copies of the very same pages, and
    indexing those would compete with the restored ones as duplicate content."""
    (DST / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /archive_original/\n"
        "Disallow: /tools/\n"
        f"\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")


def main():
    for name in GENERATED:
        target = DST / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    (DST / "melmalili").mkdir(parents=True)

    # index page: original filename kept, plus index.html so it serves as the
    # site root. Both canonicalise to the root URL, since they are the same page.
    idx = convert(SRC / "m_elmalili_index.htm", depth=0, canonical=BASE_URL,
                  description="Elmalili M.hamdi Yazir'in Turkce Kur'an meali — "
                              "114 surenin tam metni, sure indeksi.")
    (DST / "m_elmalili_index.htm").write_text(idx, encoding="utf-8")
    (DST / "index.html").write_text(idx, encoding="utf-8")

    labels = surah_labels(idx)  # {"melmalili/fatiha.htm": "1-Fatiha", ...}
    pages = sorted((SRC / "melmalili").glob("*.htm"))
    for p in pages:
        rel = f"melmalili/{p.name}"
        label = labels.get(rel, p.stem)
        (DST / rel).write_text(
            convert(p, depth=1, canonical=BASE_URL + rel,
                    description=f"{label} Suresi — Elmalili M.hamdi Yazir'in "
                                f"Turkce meali, tam metin."),
            encoding="utf-8")

    write_sitemap([f"melmalili/{p.name}" for p in pages])
    write_robots()
    print(f"index + {len(pages)} surah pages + sitemap.xml + robots.txt -> {DST}")


if __name__ == "__main__":
    main()
