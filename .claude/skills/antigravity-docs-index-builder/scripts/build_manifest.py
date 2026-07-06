#!/usr/bin/env python3
"""
Build .claude/skills/antigravity-docs/references/docs-manifest.json from the
live Antigravity web app.

Why this exists: antigravity.google/docs pages are a client-rendered SPA with no
static per-page content that a plain HTTP fetch can read. But the app ships two
useful static resources:

  1. The JS bundle (main-<hash>.js) embeds a `DOCS_STRUCTURE` array of
     {section, path, slug, filename} records — the authoritative map of doc pages.
  2. Each page's real Markdown lives at
     https://antigravity.google/assets/docs/<path>/<filename>.md
  3. llms.txt lists `- [Title](/docs/<slug>): description` for human-readable
     titles + descriptions (great for triage), keyed by the same slug.

This script downloads the bundle (NOT via a markdown-converting fetcher — the
raw JS is required), parses DOCS_STRUCTURE, enriches each entry with the
title/description from llms.txt (joined on slug), and writes the manifest that
the `antigravity-docs` skill reads.

Usage:
    python3 build_manifest.py            # rebuild; no-op if bundle unchanged
    python3 build_manifest.py --force    # rebuild even if bundle hash matches
"""
import argparse
import gzip
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

BASE = "https://antigravity.google"
# Any doc page works as the entry point to discover the current bundle name.
SEED_PAGE = f"{BASE}/docs/home"
LLMS_URL = f"{BASE}/llms.txt"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.normpath(os.path.join(
    SCRIPT_DIR, "..", "..", "antigravity-docs", "references", "docs-manifest.json"))

GENERATED_AT = os.environ.get("ANTIGRAVITY_BUILD_DATE", "").strip()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={
        "Accept-Encoding": "gzip",
        "User-Agent": "antigravity-docs-index-builder",
    })
    raw = urllib.request.urlopen(req, timeout=45).read()
    if raw[:2] == b"\x1f\x8b":  # gzip magic
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    return raw


def find_bundle_name(page_html: str) -> str:
    m = re.search(r'src="(main-[A-Za-z0-9]+\.js)"', page_html)
    if not m:
        sys.exit("ERROR: could not find main-<hash>.js in the seed page. "
                 "The app shell changed — inspect it manually.")
    return m.group(1)


def parse_structure(bundle: str):
    """Extract every {section,path,slug,filename} record, tolerant of key order."""
    obj_re = re.compile(r'\{(?:(?:section|path|slug|filename):"(?:[^"\\]|\\.)*",?){4}\}')
    key_re = re.compile(r'(section|path|slug|filename):"((?:[^"\\]|\\.)*)"')
    seen, out = set(), []
    for m in obj_re.finditer(bundle):
        d = dict(key_re.findall(m.group(0)))
        if set(d) != {"section", "path", "slug", "filename"}:
            continue
        key = (d["path"], d["filename"])
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    if not out:
        sys.exit("ERROR: DOCS_STRUCTURE not found in bundle. The build changed — "
                 "re-derive the record shape by grepping the bundle for 'filename:'.")
    return out


def parse_llms(text: str) -> dict:
    line_re = re.compile(
        r'- \[([^\]]+)\]\(https://antigravity\.google/docs/([^)]+)\):\s*(.*)')
    out = {}
    for ln in text.splitlines():
        m = line_re.match(ln.strip())
        if m:
            out[m.group(2).rstrip("/")] = {
                "title": m.group(1).strip(),
                "description": m.group(3).strip(),
            }
    return out


def title_from_filename(fn: str) -> str:
    return fn.replace("-", " ").replace("_", " ").strip().title()


def load_existing():
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def diff(old, new_pages):
    old_slugs = {p["slug"] for p in (old or {}).get("pages", [])}
    new_slugs = {p["slug"] for p in new_pages}
    added = sorted(new_slugs - old_slugs)
    removed = sorted(old_slugs - new_slugs)
    return added, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="rebuild even if the bundle hash is unchanged")
    args = ap.parse_args()

    existing = load_existing()

    print(f"Discovering bundle via {SEED_PAGE} ...")
    bundle_name = find_bundle_name(fetch(SEED_PAGE).decode("utf-8", "replace"))
    print(f"  bundle: {bundle_name}")

    if (existing and not args.force
            and existing.get("_meta", {}).get("source_bundle") == bundle_name):
        print("Bundle unchanged since last build — docs structure is up to date. "
              "Nothing to do. (Use --force to rebuild anyway.)")
        return

    bundle_bytes = fetch(f"{BASE}/{bundle_name}")
    bundle = bundle_bytes.decode("utf-8", "replace")
    print(f"  downloaded {len(bundle_bytes):,} bytes")

    struct = parse_structure(bundle)
    llms = parse_llms(fetch(LLMS_URL).decode("utf-8", "replace"))
    print(f"  DOCS_STRUCTURE pages: {len(struct)}   llms.txt entries: {len(llms)}")

    pages, unmatched = [], []
    for r in struct:
        meta = llms.get(r["slug"].rstrip("/"))
        if not meta:
            unmatched.append(r["slug"])
        pages.append({
            "section": r["section"],
            "slug": r["slug"],
            "title": (meta or {}).get("title") or title_from_filename(r["filename"]),
            "description": (meta or {}).get("description", ""),
            "content_url": f"{BASE}/assets/docs/{r['path']}/{r['filename']}.md",
        })

    if unmatched:
        print(f"  NOTE: {len(unmatched)} page(s) had no llms.txt description "
              f"(used filename-derived title): {', '.join(unmatched)}")

    manifest = {
        "_meta": {
            "generated_at": GENERATED_AT or "unknown",
            "source_bundle": bundle_name,
            "bundle_sha256": hashlib.sha256(bundle_bytes).hexdigest(),
            "index_url": LLMS_URL,
            "content_url_template": f"{BASE}/assets/docs/{{path}}/{{filename}}.md",
            "page_count": len(pages),
            "builder_skill": "antigravity-docs-index-builder",
            "note": ("Auto-generated from the Antigravity web app JS bundle "
                     "DOCS_STRUCTURE, enriched with titles/descriptions from "
                     "llms.txt. Do not hand-edit; regenerate with "
                     "/antigravity-docs-index-builder."),
        },
        "pages": pages,
    }

    added, removed = diff(existing, pages)
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nWrote {MANIFEST_PATH}")
    print(f"  pages: {len(pages)}")
    if existing:
        print(f"  added:   {added or '(none)'}")
        print(f"  removed: {removed or '(none)'}")
    else:
        print("  (first build — no previous manifest to diff against)")


if __name__ == "__main__":
    main()
