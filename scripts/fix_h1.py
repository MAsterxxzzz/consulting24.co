#!/usr/bin/env python3
"""
Repair garbled <h1> headings on the English landing pages and their zh/es/ar twins.

Background (Bing audit, 28 Sep 2026): backfill_seo_fixes.py replaced a page's old
malformed <title> string *everywhere* in the file. The old title was also the leading
part of the <h1>, so 300+ pages ended up with headings like
  "Crypto Fund License in Romania (2026): Cost & Setup Romania: Your Guide to ..."
  "MiCA License Crypto License: Complete Guide for 2026"
The translations were produced from those pages and inherited the garbage.

Rule: a landing-page H1 is garbled when it is not the title stem and either
  - matches a known garbage shape, or
  - repeats "license" (comparison "vs" pages excepted), or
  - starts with the whole title and keeps going (comparison pages excepted), or
  - is longer than 90 characters (comparison pages excepted).
Fix: H1 := <title> without the " - Consulting24" / " | C24" suffix.
Translations: H1 := the leading part of the H1 that matches the translated <title>
(same text, own casing) or, failing that, the translated <title> itself. No API calls.
Also strips the leftover "<X> Crypto License" duplicate from the Service schema "name"
and collapses "VASP License Crypto License"-style phrases in H2s and prose (all languages).

Afterwards config/translations.json is stamped with the new English digest so
translate_pages.py does not re-translate pages whose only change was this repair.

  python3 scripts/fix_h1.py            # dry run, prints what would change
  python3 scripts/fix_h1.py --apply    # write files + update translations.json
"""
import glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from content_hash import content_digest  # noqa: E402

LANGS = ("zh", "es", "ar")
SKIP = {"zh", "es", "ar", "blog", "news", "post", "config", "scripts", "img", "_files",
        "link-research", "marketing", "outreach", "research", "luxury-chauffeur-service-dubai"}
STATE = os.path.join(ROOT, "config", "translations.json")
BASE = "https://www.consulting24.co"

GARBAGE = re.compile(r"License Crypto License|Cost & Setup [A-Z]|Requirements: Your Complete|"
                     r"License License|\): Cost: |, Process [A-Z]|\): Cost [A-Z]")
SUFFIX = re.compile(r"\s*[-|]\s*(Consulting24|C24)\s*$")
H1_RE = re.compile(r"(<h1[^>]*>)(.*?)(</h1>)", re.S)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
NAME_RE = re.compile(r'"name":"([^"]*?) Crypto License"')
# "VASP License Crypto License" / "a cryptocurrency license crypto license" in H2s and prose
DUP_RE = re.compile(r"\b([A-Za-z]+ Licen[cs]e) Crypto Licen[cs]e\b", re.I)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def is_garbled(h1, stem):
    if not h1 or h1 == stem:
        return False
    low = h1.lower()
    vs = " vs " in low
    if GARBAGE.search(h1):
        return True
    if low.count("license") >= 2 and not vs:
        return True
    if low.startswith(stem.lower()) and len(h1) > len(stem) and not vs:
        return True
    if len(h1) > 90 and not vs:
        return True
    return False


def fix_en(path):
    src = read(path)
    tm = TITLE_RE.search(src); hm = H1_RE.search(src)
    if not tm or not hm:
        return None
    title_esc = SUFFIX.sub("", tm.group(1).strip())      # escaped, suffix removed
    stem = html.unescape(title_esc)
    h1 = plain(hm.group(2))
    out = src
    notes = []
    if is_garbled(h1, stem):
        out = out[:hm.start(2)] + title_esc + out[hm.end(2):]
        notes.append(f"h1: {h1[:70]!r} -> {stem!r}")
    # Service schema "name": "<Vertical> <Country> Crypto License" -> "<Vertical> <Country>"
    def _name(m):
        inner = m.group(1)
        if "license" in inner.lower() and " vs " not in inner.lower():
            notes.append(f'schema name: {m.group(0)[8:]} -> "{inner}"')
            return f'"name":"{inner}"'
        return m.group(0)
    out = NAME_RE.sub(_name, out)
    out, n = DUP_RE.subn(r"\1", out)
    if n:
        notes.append(f"text: {n} duplicate 'License Crypto License' phrase(s) collapsed")
    return (out if out != src else None), notes


def fix_translation(path):
    src = read(path)
    tm = TITLE_RE.search(src); hm = H1_RE.search(src)
    if not tm or not hm:
        return None, ""
    title_esc = SUFFIX.sub("", tm.group(1).strip())
    stem = html.unescape(title_esc)
    h1_raw = hm.group(2)
    h1 = plain(h1_raw)
    if h1 == stem:
        return None, ""
    low_h1, low_t = h1.lower(), stem.lower()
    if low_h1.startswith(low_t) and len(h1) > len(stem):
        new = h1[:len(stem)].rstrip(" :：-–|")           # keep the H1's own casing
        new_esc = html.escape(new, quote=False)
    elif low_h1 == low_t:
        return None, ""
    else:
        new = stem
        new_esc = title_esc
    out = src[:hm.start(2)] + new_esc + src[hm.end(2):]
    return out, f"{h1[:60]!r} -> {new!r}"


def main():
    apply = "--apply" in sys.argv
    changed_en, changed_tr, schema_fixes = [], [], 0
    fixed_slugs, touched_en = [], []
    for path in sorted(glob.glob(os.path.join(ROOT, "*", "index.html"))):
        slug = os.path.basename(os.path.dirname(path))
        if slug in SKIP:
            continue
        r = fix_en(path)
        if not r:
            continue
        out, notes = r
        if out is None:
            continue
        if any(n.startswith("h1:") for n in notes):
            fixed_slugs.append(slug)
            changed_en.append((slug, [n for n in notes if n.startswith("h1:")][0]))
        touched_en.append(slug)
        schema_fixes += sum(1 for n in notes if n.startswith("schema"))
        if apply:
            write(path, out)
    # translations: H1 for every page whose English H1 was repaired, duplicate phrase everywhere
    fixed_set = set(fixed_slugs)
    for lang in LANGS:
        for p in sorted(glob.glob(os.path.join(ROOT, lang, "*", "index.html"))):
            slug = os.path.basename(os.path.dirname(p))
            out, note = (fix_translation(p) if slug in fixed_set else (None, ""))
            cur = out if out is not None else read(p)
            cur2, n = DUP_RE.subn(r"\1", cur)
            if n:
                note = (note + "; " if note else "") + f"{n} duplicate phrase(s) collapsed"
                out = cur2
            if out is not None and out != read(p):
                changed_tr.append((f"{lang}/{slug}", note))
                if apply:
                    write(p, out)
    # stamp translations.json with the new English digest for repaired pages
    stamped = 0
    if apply and touched_en:
        with open(STATE, encoding="utf-8") as f:
            st = json.load(f)
        for slug in touched_en:
            url = f"{BASE}/{slug}/"
            rec = st.get(url)
            if not rec:
                continue
            digest = content_digest(read(os.path.join(ROOT, slug, "index.html")))
            for lang in LANGS:
                if lang in rec and os.path.exists(os.path.join(ROOT, lang, slug, "index.html")):
                    rec[lang]["src"] = digest; stamped += 1
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
    mode = "APPLIED" if apply else "DRY RUN"
    print(f"[{mode}] English H1 repaired: {len(changed_en)} | schema names cleaned: {schema_fixes} | "
          f"translated H1 repaired: {len(changed_tr)} | translation digests stamped: {stamped}")
    if "--verbose" in sys.argv or not apply:
        for slug, n in changed_en:
            print(f"  {slug}: {n}")
        for k, n in changed_tr[:60]:
            print(f"  {k}: {n}")
        if len(changed_tr) > 60:
            print(f"  ... {len(changed_tr) - 60} more translated pages")


if __name__ == "__main__":
    main()
