#!/usr/bin/env python3
"""
Fidelity check: every restored page in site/ must carry exactly the same visible
text as its raw archive_original/ counterpart.

The comparison strips markup, the Wayback injection, the removed <script> blocks
and the added footer line, then requires a character-for-character match of what
is left. Any difference means the restoration altered the meal text and is a bug.
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "archive_original"
DST = ROOT

DROP = re.compile(r'<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->', re.S | re.I)
TAGS = re.compile(r'<[^>]+>')
# The footer adds one word of visible text, always as the last thing on the page.
# Anchoring to the end keeps a genuine "Kaynak" inside the meal text from being
# silently swallowed by this check.
FOOTER_TEXT = re.compile(r'\s*Kaynak\s*$')

# The one piece of visible text deliberately dropped from the original: the
# index page's "kaynak: kuranikerim.com" credit. Removed from both sides of the
# comparison so the rest of the page is still held to exact equality.
REMOVED_CREDIT = re.compile(r'\s*kaynak:\s*kuranikerim\.com', re.I)


def visible(html: str) -> str:
    html = DROP.sub(" ", html)
    text = TAGS.sub(" ", html)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r'\s+', " ", text).strip()
    text = REMOVED_CREDIT.sub("", text)
    return FOOTER_TEXT.sub("", text)


def check(name: str, raw: Path, restored: Path) -> bool:
    a = visible(raw.read_bytes().decode("cp1254"))
    b = visible(restored.read_text(encoding="utf-8"))
    if a == b:
        return True
    print(f"MISMATCH  {name}")
    for i, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            print(f"    first difference at char {i}")
            print(f"    archive : …{a[max(0, i-60):i+60]}…")
            print(f"    restored: …{b[max(0, i-60):i+60]}…")
            break
    else:
        print(f"    length differs: archive {len(a)} vs restored {len(b)}")
        longer, tail = (a, a[len(b):]) if len(a) > len(b) else (b, b[len(a):])
        print(f"    extra text: …{tail[:160]}…")
    return False


def main() -> int:
    expected = [ln.strip() for ln in (ROOT / "links.txt").read_text().splitlines() if ln.strip()]
    failures = 0

    missing = [p for p in expected if not (SRC / p).exists()]
    if missing:
        print(f"!! {len(missing)} page(s) never downloaded: {', '.join(missing[:8])}"
              f"{' …' if len(missing) > 8 else ''}")
        failures += len(missing)

    if not check("m_elmalili_index.htm", SRC / "m_elmalili_index.htm",
                 DST / "m_elmalili_index.htm"):
        failures += 1

    for rel in expected:
        raw, restored = SRC / rel, DST / rel
        if not raw.exists():
            continue
        if not restored.exists():
            print(f"MISSING   {rel} not present in site/")
            failures += 1
        elif not check(rel, raw, restored):
            failures += 1

    # the index must still link to all 114 surahs, and each target must exist
    idx = (DST / "index.html").read_text(encoding="utf-8")
    links = re.findall(r'href="(melmalili/[^"]+)"', idx)
    print(f"\nindex links: {len(links)} (expected 114)")
    broken = [l for l in links if not (DST / l).exists()]
    if broken:
        print(f"broken links: {len(broken)} -> {', '.join(broken[:8])}")
        failures += len(broken)

    # nothing should reference the removed images or the wayback host.
    # Only generated pages are checked — archive_original/ holds the raw
    # snapshots, which of course still carry those references.
    generated = ([DST / "index.html", DST / "m_elmalili_index.htm"]
                 + sorted((DST / "melmalili").glob("*.htm")))
    stray = [p.name for p in generated
             if re.search(r'web\.archive|/web/\d{14}|\.(?:gif|jpe?g|png)\b',
                          p.read_text(encoding="utf-8"), re.I)]
    if stray:
        print(f"pages with stray asset/wayback refs: {len(stray)} -> {stray[:8]}")
        failures += len(stray)

    # sitemap must list the root plus every surah page that actually exists,
    # and every canonical tag must agree with the sitemap's own base URL
    sitemap = (DST / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r'<loc>([^<]+)</loc>', sitemap)
    base = locs[0] if locs else ""
    listed = {l[len(base):] for l in locs if l != base}
    on_disk = {f"melmalili/{p.name}" for p in (DST / "melmalili").glob("*.htm")}
    print(f"sitemap URLs: {len(locs)} (expected {len(on_disk) + 1})")
    if listed != on_disk:
        for extra in sorted(listed - on_disk):
            print(f"sitemap lists a page that does not exist: {extra}")
        for gap in sorted(on_disk - listed):
            print(f"page missing from sitemap: {gap}")
        failures += len(listed ^ on_disk)

    missing_canonical = [p for p in generated
                         if f'rel="canonical" href="{base}' not in
                         p.read_text(encoding="utf-8")]
    if missing_canonical:
        print(f"pages without a canonical tag matching {base}: "
              f"{[p.name for p in missing_canonical]}")
        failures += len(missing_canonical)

    print("\nOK — text identical on every page, sitemap and canonicals consistent"
          if failures == 0 else f"\n{failures} problem(s) found")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
