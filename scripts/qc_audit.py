import html
#!/usr/bin/env python3
"""
qc_audit.py — audit EVERY published page against the Consulting24 QC checklist.
Run in the daily pipeline after publishing; reports any page below standard so it
can be regenerated. Complements the generation-time gate (catches drift / old pages).

  python3 scripts/qc_audit.py            # report all
  python3 scripts/qc_audit.py --fail     # exit 1 if any page fails (for CI/daily gate)
Thresholds: >=2000 words, >=3 images, >=5 FAQs, >=5 internal links, homepage link,
title 50-65, desc 110-165, canonical + Service/FAQ schema present.
"""
import os, re, glob, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def audit(path):
    h = open(path, encoding="utf-8").read()
    body = h.split("<body", 1)[-1]
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S)
    text = re.sub("<[^>]+>", " ", text)
    words = len(text.split())
    title = (re.search(r"<title>(.*?)</title>", h, re.S) or [None, ""])[1].strip()
    desc = (re.search(r'<meta name="description" content="(.*?)"', h, re.S) or [None, ""])[1]
    faqs = h.count('"@type":"Question"')
    images = h.count("<img ")
    internal = len(set(re.findall(r'href="(/[^"#?]*)"', h)))
    fails = []
    if words < 2000: fails.append(f"words {words}")
    if images < 3: fails.append(f"img {images}")
    if faqs < 5: fails.append(f"faq {faqs}")
    if internal < 5: fails.append(f"links {internal}")
    if 'href="/"' not in h: fails.append("no-home-link")
    if not (50 <= len(title) <= 65): fails.append(f"title {len(title)}")
    h1 = html.unescape(re.sub(r"<[^>]+>", "", (re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S) or [None, ""])[1])).strip()
    h1l = h1.lower()
    stem = html.unescape(re.sub(r"\s*[-|]\s*(Consulting24|C24)\s*$", "", title)).lower()
    # garbled heading guard (28 Sep 2026, scripts/fix_h1.py): a title pasted in front of
    # the old H1, a repeated "license", or an over-long heading. Comparison ("vs") pages
    # excepted; blog/news headlines legitimately extend their trimmed <title>.
    is_post = "/blog/" in path or "/news/" in path
    if " vs " not in h1l and h1l != stem:
        if h1l.count("license") >= 2: fails.append("h1 repeats license")
        if len(h1) > 90: fails.append(f"h1 {len(h1)}")
        if stem and not is_post and h1l.startswith(stem) and len(h1l) > len(stem): fails.append("h1 title+tail")
    if not (110 <= len(desc) <= 165): fails.append(f"desc {len(desc)}")
    if "canonical" not in h: fails.append("no-canonical")
    if '"FAQPage"' not in h: fails.append("no-faq-schema")
    return words, fails

def main():
    rel = lambda p: "/" + os.path.relpath(p, ROOT)
    pages = sorted(glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True))
    # skip the homepage + the hub/blog index (different page types, hand-built)
    # exclude the homepage + listing/hub pages (navigational, not long-form content)
    skip = {os.path.join(ROOT, p) for p in ("index.html", "blog/index.html", "jurisdictions/index.html")}
    failed = []
    for p in pages:
        if p in skip: continue
        words, fails = audit(p)
        if fails:
            failed.append((rel(p), words, fails))
    home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    for tag in ("yandex-verification", "google-site-verification"):
        if f'name="{tag}"' not in home:
            failed.append(("/", 0, [f"homepage lost the {tag} meta tag (Webmaster rights)"]))
    print(f"QC audit: {len(pages)} pages | {len(failed)} below standard")
    for u, w, f in failed:
        print(f"  FAIL {u}  -> {', '.join(f)}")
    if "--fail" in sys.argv and failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
