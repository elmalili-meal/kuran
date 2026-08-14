#!/bin/bash
# Downloads the raw Wayback Machine snapshot of enfal.de/m_elmalili_index.htm
# into archive_original/ (untouched, wayback-injected copies kept as evidence).
set -u
BASE="https://web.archive.org/web/20240919080311"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/archive_original"
mkdir -p "$OUT/melmalili"

# web.archive.org rate-limits aggressively, so pace requests and retry patiently.
DELAY="${DELAY:-4}"

fetch () { # $1 = path relative to enfal.de, $2 = wayback modifier ("" or "im_")
  local path="$1" mod="${2:-}" dest="$OUT/$1"
  [ -s "$dest" ] && return 0
  local code
  code=$(curl -sL --max-time 120 --retry 5 --retry-delay 10 --retry-all-errors \
         -o "$dest" -w "%{http_code}" "$BASE$mod/http://enfal.de/$path")
  echo "$code  $path"
  [ "$code" = "200" ] || { rm -f "$dest"; sleep 15; return 1; }
  sleep "$DELAY"
}

missing () {
  local n=0
  while read -r p; do
    [ -n "$p" ] && [ ! -s "$OUT/$p" ] && n=$((n + 1))
  done < "$ROOT/links.txt"
  echo "$n"
}

fetch "m_elmalili_index.htm"

# The original site's six banner images (ustb.gif, altb.gif, kucuk_kuran1.jpg,
# kuran1.jpg, bismillah.jpg, kabe_resim1.jpg) are deliberately NOT fetched:
# this is a text-only restoration and their rights status is unknown.

# several passes: each one only retries what is still missing
for pass in 1 2 3 4 5 6; do
  left=$(missing)
  [ "$left" -eq 0 ] && break
  echo "== pass $pass — $left page(s) missing =="
  while read -r p; do
    [ -n "$p" ] && fetch "$p"
  done < "$ROOT/links.txt"
done

echo "DONE — $(missing) page(s) still missing"
