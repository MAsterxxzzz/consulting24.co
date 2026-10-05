#!/usr/bin/env python3
"""
table_wrap.py — keep every data table inside its horizontal-scroll box.

styles.css gives every <table> min-width:520px; only the <div class="t-wrap"> around it
(overflow-x:auto) stops a wide table from widening the whole page on a phone. DeepSeek's
section HTML (generate.py) came back with bare <table class="t-wrap-inner">, so on
24 Sep 2026 ~1,740 English and ~1,140 tables per language (ar/es/zh) had no box, and a
375px phone laid /ar/dubai-crypto-license/ out 540px wide.

  wrap_tables(html) -> (html, n)          used by generate.py and translate_pages.py
  python3 scripts/table_wrap.py           wrap bare tables in every site page (idempotent)
  python3 scripts/table_wrap.py --check   list pages with bare tables, exit 1 if any
  python3 scripts/table_wrap.py FILE ...  only these files

A table already inside a scroll container (.t-wrap, .cmp-table-wrap, or a div with an
inline overflow:auto) is left alone. The wrapper is emitted tight,
<div class="t-wrap"><table ...>...</table></div>, and content_hash.py hashes that form
away, so wrapping bumps no sitemap <lastmod> and triggers no re-translation.
"""
import os, re, sys, subprocess
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPEN, CLOSE = '<div class="t-wrap">', "</div>"
_SCROLL_CLASSES = {"t-wrap", "cmp-table-wrap"}
_OVERFLOW = re.compile(r"overflow(?:-x)?\s*:\s*(?:auto|scroll)", re.I)


def _scrolls(attrs):
    a = dict(attrs)
    return bool(_SCROLL_CLASSES & set((a.get("class") or "").split())) or \
        bool(_OVERFLOW.search(a.get("style") or ""))


class _BareTables(HTMLParser):
    """(start, end) offsets of each outermost <table> that no scroll container encloses.
    Only <div> and <table> are tracked: both always need an explicit end tag, so the
    stacks stay right on real-world markup that leaves <p>/<li> open."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.text = text
        self.line_at = [0] + [m.end() for m in re.finditer("\n", text)]
        self.divs, self.tables, self.spans = [], [], []

    def _pos(self):
        line, col = self.getpos()
        return self.line_at[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            self.divs.append(_scrolls(attrs))
        elif tag == "table":
            bare = not self.tables and not any(self.divs)
            self.tables.append(self._pos() if bare else None)

    def handle_endtag(self, tag):
        if tag == "div" and self.divs:
            self.divs.pop()
        elif tag == "table" and self.tables:
            start = self.tables.pop()
            if start is not None:
                self.spans.append((start, self.text.index(">", self._pos()) + 1))


def bare_tables(html):
    p = _BareTables(html)
    p.feed(html)
    p.close()
    return p.spans


def wrap_tables(html):
    """Wrap every bare table in <div class="t-wrap">. Returns (html, number wrapped)."""
    spans = bare_tables(html)
    for start, end in reversed(spans):
        seg = html[start:end]
        if not (seg[:6].lower() == "<table" and seg[-8:].lower() == "</table>"):
            raise ValueError(f"table offsets off at {start}: {seg[:40]!r}...{seg[-40:]!r}")
        html = html[:start] + OPEN + seg + CLOSE + html[end:]
    return html, len(spans)


def site_pages():
    """Every tracked or new (not ignored) .html file in the repo."""
    out = subprocess.check_output(["git", "-C", ROOT, "ls-files", "--cached", "--others",
                                   "--exclude-standard", "*.html"], text=True)
    return [os.path.join(ROOT, p) for p in out.splitlines()]


def main(argv):
    check = "--check" in argv
    paths = [a for a in argv if not a.startswith("--")] or site_pages()
    pages = tables = 0
    for path in paths:
        with open(path, encoding="utf-8", newline="") as f:
            html = f.read()
        if "<table" not in html.lower():
            continue
        new, n = wrap_tables(html)
        if not n:
            continue
        pages += 1; tables += n
        if check:
            print(f"{n:4d} bare  {os.path.relpath(path, ROOT)}")
        else:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
    print(f"{tables} {'bare' if check else 'wrapped'} tables in {pages} pages")
    return 1 if check and tables else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
