#!/usr/bin/env python3
"""
Probe a documentation site for (a) the cheapest lazy-loadable index and
(b) the cheapest plain-text content contract, and emit a machine-readable
fact sheet that `docs-skill-builder` turns into an `xxx-docs` skill.

This script only MEASURES. It never crawls a page list, never writes a
manifest, and never decides anything — the decision table lives in
references/mechanism-catalog.md and is applied by the agent.

Why a calibrated 404 matters: many docs sites answer 200 for every path, or
serve a fixed-size HTML error page. Comparing a candidate against a
deliberately bogus URL is the only reliable way to tell "this file exists"
from "this site swallows everything". Measured on docs.databricks.com, whose
404 page is a consistent 12,999-byte text/html body served under status 404,
and whose `<page>.md` twins do not exist at all.

Usage:
    python3 probe_docs_source.py https://docs.databricks.com
    python3 probe_docs_source.py https://docs.databricks.com --json facts.json
    python3 probe_docs_source.py https://vercel.com/docs --extra https://vercel.com/docs/llms.txt
"""
import argparse
import gzip
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "docs-skill-builder-probe (+one-off documentation capability probe)"
DEFAULT_BUDGET = 28
DEFAULT_DELAY = 0.2
BODY_CAP = 4_000_000          # never hold more than 4 MB of any one response
SITEMAP_SCAN_CAP = 2_000_000  # stream at most 2 MB when counting <loc> entries

# `- [Title](url): desc`  /  `- [Title](url) - desc`  /  `- [Title](url)`
ENTRY_RE = re.compile(r'^\s*[-*]\s*\[([^\]]*)\]\(\s*([^)\s]+)[^)]*\)\s*(?:([:—-])\s*(.*))?$')
LOC_RE = re.compile(r'<loc>\s*([^<]+?)\s*</loc>', re.I)
SITEMAP_DIRECTIVE_RE = re.compile(r'^\s*sitemap:\s*(\S+)', re.I | re.M)


class Budget(Exception):
    pass


class Fetcher:
    """Throttled, budgeted, redirect-following fetcher. Pure stdlib."""

    def __init__(self, budget=DEFAULT_BUDGET, delay=DEFAULT_DELAY, timeout=30):
        self.budget = budget
        self.delay = delay
        self.timeout = timeout
        self.count = 0
        self._last = 0.0

    def get(self, url, headers=None, cap=BODY_CAP):
        """Return dict(url, status, ctype, final_url, bytes, body, error)."""
        if self.count >= self.budget:
            raise Budget(f"request budget of {self.budget} exhausted at {url}")
        gap = self.delay - (time.time() - self._last)
        if gap > 0:
            time.sleep(gap)
        self.count += 1
        self._last = time.time()

        hdrs = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, headers=hdrs)
        out = {"url": url, "status": None, "ctype": "", "final_url": url,
               "bytes": 0, "body": "", "error": None}
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                raw = r.read(cap)
                out["status"] = r.status
                out["ctype"] = (r.headers.get("Content-Type") or "").split(";")[0].strip()
                out["final_url"] = r.geturl()
        except urllib.error.HTTPError as e:
            raw = e.read(cap)
            out["status"] = e.code
            out["ctype"] = (e.headers.get("Content-Type") or "").split(";")[0].strip()
            out["final_url"] = e.url or url
        except Exception as e:  # URLError, timeout, ssl, ...
            out["error"] = f"{type(e).__name__}: {e}"
            return out

        if raw[:2] == b"\x1f\x8b":
            try:
                raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
            except OSError:
                pass
        out["bytes"] = len(raw)
        out["body"] = raw.decode("utf-8", "replace")
        return out


def norm_sig(body):
    """Signature that ignores the one path that differs between two 404 bodies."""
    return hashlib.sha256(re.sub(r'\s+', ' ', body).encode("utf-8", "replace")).hexdigest()[:16]


def origins_for(url):
    """Candidate roots to probe, nearest first: the given path, its parents, the host."""
    p = urllib.parse.urlsplit(url if "://" in url else "https://" + url)
    host = f"{p.scheme}://{p.netloc}"
    seen, out = set(), []
    parts = [seg for seg in p.path.split("/") if seg]
    for i in range(len(parts), -1, -1):
        base = host + ("/" + "/".join(parts[:i]) if i else "")
        if base not in seen:
            seen.add(base)
            out.append(base)
    return out


INDEX_NAMES = ["llms.txt", "llms-full.txt", ".well-known/llms.txt"]


def calibrate(fetch, origin):
    """Fetch a URL that cannot exist, to learn what 'missing' looks like here."""
    bogus = f"{origin.rstrip('/')}/__docs_skill_builder_probe_404__/x"
    r = fetch.get(bogus)
    return {"probe_url": bogus, "status": r["status"], "bytes": r["bytes"],
            "ctype": r["ctype"], "sig": norm_sig(r["body"]) if r["body"] else None,
            "error": r["error"]}


def exists(r, cal):
    """True when a response is meaningfully different from this site's 404."""
    if r["error"] or r["status"] != 200 or r["bytes"] == 0:
        return False
    # A redirect into a login page is a 200 that proves nothing about the file.
    if AUTH_WALL_RE.search(urllib.parse.urlsplit(r["final_url"]).path):
        return False
    if cal.get("sig") and norm_sig(r["body"]) == cal["sig"]:
        return False
    if cal.get("status") == 200 and cal.get("bytes") and abs(r["bytes"] - cal["bytes"]) < 64:
        return False
    return True


def looks_like_index(body):
    """ENTRY_RE is anchored with ^/$, so it must be applied per line -- running
    .search() over the whole body silently matches only the first line."""
    head = body.lstrip()[:2000]
    if head[:1] == "<" or "<html" in head[:400].lower():
        return False
    for line in body.splitlines()[:4000]:
        if ENTRY_RE.match(line.strip()):
            return True
    return head.startswith("#")


AUTH_WALL_RE = re.compile(r'/(login|signin|sign-in|auth|sso)\b', re.I)


def analyze_index(body):
    """Structure + description-coverage stats that drive the mechanism choice."""
    lines = body.splitlines()
    sections, cur = [], {"name": "(root)", "entries": 0, "bytes": 0}
    entries, hosts, seps = [], {}, {}
    prose = terse = bare = 0
    md_targets = 0

    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            if cur["entries"]:
                sections.append(cur)
            cur = {"name": s[3:].strip(), "entries": 0, "bytes": 0}
            continue
        m = ENTRY_RE.match(s)
        if not m:
            continue
        title, url, sep, desc = m.group(1), m.group(2), m.group(3), (m.group(4) or "").strip()
        cur["entries"] += 1
        cur["bytes"] += len(line) + 1
        entries.append(url)
        if sep:
            seps[sep] = seps.get(sep, 0) + 1
        words = len(desc.split())
        if words >= 4:
            prose += 1
        elif words:
            terse += 1
        else:
            bare += 1
        if url.split("?")[0].rstrip("/").endswith(".md"):
            md_targets += 1
        h = urllib.parse.urlsplit(url).netloc
        if h:
            hosts[h] = hosts.get(h, 0) + 1
    if cur["entries"]:
        sections.append(cur)

    n = len(entries) or 1
    return {
        "bytes": len(body.encode("utf-8")),
        "lines": len(lines),
        "entry_count": len(entries),
        "section_count": len(sections),
        "sections": sorted(sections, key=lambda s: -s["bytes"]),
        "entry_separator": max(seps, key=seps.get) if seps else None,
        "description_prose_pct": round(100 * prose / n),
        "description_terse_pct": round(100 * terse / n),
        "description_bare_pct": round(100 * bare / n),
        "targets_are_md_pct": round(100 * md_targets / n),
        "hosts": dict(sorted(hosts.items(), key=lambda kv: -kv[1])[:5]),
        "sample_targets": entries[:40],
    }


CONTENT_VARIANTS = [
    ("as-is", "{u}", None),
    ("md-suffix", "{s}.md", None),
    ("index-md", "{s}/index.md", None),
    ("txt-suffix", "{s}.txt", None),
    ("accept-markdown", "{u}", {"Accept": "text/markdown"}),
    ("plain-query", "{u}{q}plain=1", None),
]


def probe_content(fetch, sample_url, cal):
    """Try each known plain-text convention against one real page."""
    s = sample_url.rstrip("/")
    q = "&" if "?" in sample_url else "?"
    # A path-less URL (https://host/) would turn "{s}.md" into "https://host.md",
    # an invalid host that fails as a DNS error rather than a useful 404.
    has_path = urllib.parse.urlsplit(sample_url).path.strip("/") != ""
    results, html_bytes = [], None
    for name, tmpl, headers in CONTENT_VARIANTS:
        if not has_path and "{s}" in tmpl:
            results.append({"variant": name, "url": None,
                            "skipped": "sample URL has no path; suffix variant "
                                       "would produce an invalid host"})
            continue
        url = tmpl.format(u=sample_url, s=s, q=q)
        try:
            r = fetch.get(url, headers=headers)
        except Budget as e:
            results.append({"variant": name, "url": url, "skipped": str(e)})
            break
        ok = exists(r, cal)
        body_head = r["body"].lstrip()[:200]
        is_html = "<html" in r["body"][:1500].lower() or body_head.startswith("<!")
        markdown = ok and not is_html and (
            r["ctype"] in ("text/markdown", "text/plain", "text/x-markdown")
            or body_head.startswith("#") or "\n#" in r["body"][:2000])
        if name == "as-is" and ok:
            html_bytes = r["bytes"]
        results.append({
            "variant": name, "url": url, "status": r["status"], "ctype": r["ctype"],
            "bytes": r["bytes"], "exists": ok, "is_html": is_html,
            "plain_text": bool(markdown),
            "saving_vs_html": (round(1 - r["bytes"] / html_bytes, 2)
                               if markdown and html_bytes else None),
            "error": r["error"],
        })
    return results


def probe_sitemap(fetch, origin, cal):
    """Locate a sitemap and count <loc> entries without downloading the world."""
    found = []
    robots = None
    try:
        r = fetch.get(f"{origin.rstrip('/')}/robots.txt")
        if exists(r, cal):
            robots = {"url": r["final_url"], "bytes": r["bytes"],
                      "sitemaps": SITEMAP_DIRECTIVE_RE.findall(r["body"])[:5],
                      "disallow_all": bool(re.search(r'^\s*disallow:\s*/\s*$',
                                                     r["body"], re.I | re.M))}
            found.extend(robots["sitemaps"])
    except Budget:
        pass

    for cand in [f"{origin.rstrip('/')}/sitemap.xml", f"{origin.rstrip('/')}/sitemap_index.xml"]:
        if cand not in found:
            found.append(cand)

    out = []
    for url in found[:3]:
        try:
            r = fetch.get(url, cap=SITEMAP_SCAN_CAP)
        except Budget:
            break
        if not exists(r, cal):
            out.append({"url": url, "status": r["status"], "exists": False})
            continue
        locs = LOC_RE.findall(r["body"])
        is_index = "<sitemapindex" in r["body"][:2000].lower()
        out.append({
            "url": r["final_url"], "status": r["status"], "bytes": r["bytes"],
            "exists": True, "is_sitemap_index": is_index,
            "loc_count": len(locs), "truncated": r["bytes"] >= SITEMAP_SCAN_CAP,
            "sample": locs[:5],
        })
    return {"robots": robots, "sitemaps": out}


def human(facts):
    L = []
    a = L.append
    a(f"probe target : {facts['target']}")
    a(f"requests used: {facts['requests_used']}")
    cal = facts["calibration"]
    a(f"404 signature: status={cal['status']} bytes={cal['bytes']} ctype={cal['ctype']}"
      + ("   <-- WARNING: site answers 200 for missing paths" if cal["status"] == 200 else ""))
    a("")
    a("INDEX CANDIDATES")
    if not facts["indexes"]:
        a("  none found (no llms.txt at any probed origin)")
    for ix in facts["indexes"]:
        a(f"  {ix['url']}")
        st = ix.get("stats")
        if not st:
            a(f"    exists={ix['exists']} status={ix['status']} bytes={ix['bytes']}"
              f" index_like={ix['index_like']}")
            continue
        a(f"    {st['bytes']:,} bytes | ~{st['bytes']//4:,} tokens | {st['entry_count']} entries"
          f" | {st['section_count']} sections | sep={st['entry_separator']!r}")
        a(f"    descriptions: {st['description_prose_pct']}% prose /"
          f" {st['description_terse_pct']}% terse / {st['description_bare_pct']}% bare")
        a(f"    link targets end in .md: {st['targets_are_md_pct']}% | hosts: {st['hosts']}")
        if st["sections"]:
            a("    heaviest sections:")
            for s in st["sections"][:6]:
                a(f"      {s['bytes']:>7,} B  {s['entries']:>4} entries  {s['name']}")
    a("")
    a("CONTENT CONTRACT")
    for probe in facts["content"]:
        a(f"  sample: {probe['sample']}")
        for r in probe["results"]:
            if "skipped" in r:
                a(f"    {r['variant']:<16} SKIPPED ({r['skipped']})")
                continue
            flag = "PLAIN-TEXT" if r["plain_text"] else ("html" if r["exists"] else "-")
            save = f" saves {int(r['saving_vs_html']*100)}% vs HTML" if r.get("saving_vs_html") else ""
            note = f"  ({r['error']})" if r.get("error") else ""
            a(f"    {r['variant']:<16} {str(r['status']):<4} {r['bytes']:>8,} B  {flag}{save}{note}")
    cov = facts.get("index_coverage")
    if cov:
        a("")
        a(f"INDEX COVERAGE: {cov['index_entries']} index entries vs {cov['sitemap_urls']} "
          f"sitemap URLs ({cov['ratio']:.1%}) -> {cov['verdict'].upper()}")
    a("")
    a("SITEMAP / ROBOTS")
    sm = facts["sitemap"]
    if sm.get("robots"):
        a(f"  robots.txt: {sm['robots']['url']} disallow_all={sm['robots']['disallow_all']}"
          f" sitemaps={sm['robots']['sitemaps']}")
    for s in sm.get("sitemaps", []):
        if s.get("exists"):
            a(f"  {s['url']}: {s['loc_count']} <loc>"
              f"{' (sitemap index)' if s['is_sitemap_index'] else ''}"
              f"{' [TRUNCATED]' if s.get('truncated') else ''}")
        else:
            a(f"  {s['url']}: absent (status {s.get('status')})")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="docs entry URL, e.g. https://docs.databricks.com")
    ap.add_argument("--extra", action="append", default=[],
                    help="additional index URL to probe (repeatable); use for a "
                         "location found by web search rather than URL guessing")
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                    help=f"max HTTP requests (default {DEFAULT_BUDGET})")
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="seconds between requests")
    ap.add_argument("--samples", type=int, default=1,
                    help="how many index entries to test the content contract against")
    ap.add_argument("--json", help="also write the fact sheet to this path")
    args = ap.parse_args()

    fetch = Fetcher(budget=args.budget, delay=args.delay)
    origins = origins_for(args.target)
    facts = {"target": args.target, "origins_probed": origins,
             "generated_at": os.environ.get("DOCS_PROBE_DATE", "").strip() or "unset",
             "indexes": [], "content": [], "sitemap": {}, "notes": []}

    facts["calibration"] = calibrate(fetch, origins[0])
    if facts["calibration"]["status"] == 200:
        facts["notes"].append(
            "Site returns 200 for nonexistent paths; existence was decided by "
            "body signature, not status code.")

    candidates = list(args.extra)
    for o in origins:
        for name in INDEX_NAMES:
            candidates.append(f"{o.rstrip('/')}/{name}")
    seen = set()
    try:
        for url in candidates:
            if url in seen:
                continue
            seen.add(url)
            r = fetch.get(url)
            ok = exists(r, facts["calibration"])
            rec = {"url": r["final_url"], "requested": url, "status": r["status"],
                   "bytes": r["bytes"], "ctype": r["ctype"], "exists": ok,
                   "index_like": ok and looks_like_index(r["body"]), "error": r["error"]}
            if rec["index_like"]:
                rec["stats"] = analyze_index(r["body"])
            facts["indexes"].append(rec)
    except Budget as e:
        facts["notes"].append(str(e))

    for i in facts["indexes"]:
        if i.get("exists") and i["bytes"] > 400_000:
            facts["notes"].append(
                f"{i['url']} is {i['bytes']:,} bytes (~{i['bytes']//4:,} tokens). Never load "
                f"it into context; it is only usable through a filtering pipe, if at all. "
                f"Full-text dumps (llms-full.txt) are almost always the wrong source.")

    real = [i for i in facts["indexes"] if i.get("index_like")]
    if len(real) > 1:
        facts["notes"].append(
            "More than one llms.txt found. Prefer the one whose entry hosts match the "
            "docs host; a marketing-site llms.txt often shadows the docs one "
            "(observed on databricks.com vs docs.databricks.com).")

    samples = []
    if real:
        # A full-text dump (llms-full.txt) usually has the most "entries" but is
        # the worst index; prefer a normally-sized one.
        sane = [i for i in real if i["bytes"] <= 400_000] or real
        best = max(sane, key=lambda i: i["stats"]["entry_count"])
        tgt = urllib.parse.urlsplit(args.target if "://" in args.target
                                    else "https://" + args.target)
        prefix = "/" + tgt.path.strip("/").split("/")[0] if tgt.path.strip("/") else ""

        def rank(u):
            p = urllib.parse.urlsplit(u)
            if not u.startswith("http") or not p.path.strip("/"):
                return None
            # In-scope leaf on the docs host beats anything else: a probe against
            # an off-topic page (marketplace, blog) measures the wrong contract.
            score = 0
            if p.netloc == tgt.netloc:
                score += 2
            if prefix and p.path.startswith(prefix):
                score += 4
            if p.path.strip("/").count("/") >= 1:
                score += 1
            return score

        scored = [(rank(u), u) for u in best["stats"]["sample_targets"]]
        scored = [(s, u) for s, u in scored if s is not None]
        scored.sort(key=lambda su: -su[0])
        seen_s = set()
        samples = [u for _, u in scored if not (u in seen_s or seen_s.add(u))][:args.samples]
        facts["index_chosen_for_sampling"] = best["url"]
    if not samples:
        samples = [args.target]
    for s in samples:
        try:
            facts["content"].append({"sample": s, "results": probe_content(fetch, s, facts["calibration"])})
        except Budget as e:
            facts["notes"].append(str(e))
            break

    try:
        facts["sitemap"] = probe_sitemap(fetch, origins[0], facts["calibration"])
    except Budget as e:
        facts["notes"].append(str(e))

    # Hub-vs-leaf: an index with far fewer entries than the site has pages is a
    # curated hub list, so the site already provides a second level to descend
    # into. Measured on Databricks: 252 index entries vs 5,645 sitemap URLs.
    biggest_map = max((s.get("loc_count", 0) for s in facts["sitemap"].get("sitemaps", [])
                       if s.get("exists") and not s.get("is_sitemap_index")), default=0)
    if real and biggest_map:
        n_entries = max(i["stats"]["entry_count"] for i in real)
        facts["index_coverage"] = {
            "index_entries": n_entries, "sitemap_urls": biggest_map,
            "ratio": round(n_entries / biggest_map, 3),
            "verdict": "leaf-level" if n_entries >= 0.6 * biggest_map else "hub-level",
        }
        if facts["index_coverage"]["verdict"] == "hub-level":
            facts["notes"].append(
                f"Index lists {n_entries} entries but the sitemap has {biggest_map} URLs "
                f"({facts['index_coverage']['ratio']:.1%}) — the index is a curated hub "
                f"list, not a full page list. Plan a second hop (index -> landing page -> "
                f"its links) rather than assuming the index is exhaustive.")

    facts["requests_used"] = fetch.count
    print(human(facts))
    if facts["notes"]:
        print("\nNOTES")
        for n in facts["notes"]:
            print(f"  - {n}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(facts, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\nfact sheet -> {args.json}")


if __name__ == "__main__":
    sys.exit(main())
