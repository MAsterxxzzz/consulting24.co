#!/usr/bin/env python3
"""
indexnow.py — the ONE IndexNow submitter for www.consulting24.co (spec: indexnow.org/documentation).

publish.py only QUEUES changed/new/removed URLs (config/indexnow_queue.json). This script drains
the queue AFTER the deploy, and only submits a URL once the live site already serves what the
local build produced:
  - page      -> live content_digest == config/page_hashes.json hash (the new version is deployed)
  - redirect  -> live response is the generated redirect stub (config/redirects.json source)
  - removed   -> live 404/410, or a redirect stub / noindex page
Anything else stays queued (Pages still building, CDN still stale, or the change is on an unmerged
branch) and is re-checked on the next flush.

Why (audit 2026-09-26): publish.py used to ping inside the build, BEFORE `git push c24est`, so
Bing/Yandex fetched new posts as 404 and changed pages in their old version; a publish.py run on a
PR branch pinged URLs days before they went live.

  python3 scripts/indexnow.py flush [--wait SECONDS]   # submit what is live (poll up to SECONDS)
  python3 scripts/indexnow.py flush --dry-run          # show what would be submitted, change nothing
  python3 scripts/indexnow.py status                   # queue / today's count / key file check
  python3 scripts/indexnow.py add URL [URL ...]        # queue URLs by hand (same host only)
"""
import os, sys, json, time, datetime, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from content_hash import content_digest

HOST = "www.consulting24.co"
BASE = f"https://{HOST}"
CAP = int(os.environ.get("INDEXNOW_CAP", "200"))          # URLs per calendar day
QUEUE = os.path.join(ROOT, "config", "indexnow_queue.json")
LOG = os.path.join(ROOT, "config", "indexnow_submitted.json")
HASHES = os.path.join(ROOT, "config", "page_hashes.json")
REDIRECTS = os.path.join(ROOT, "config", "redirects.json")
REDIRECT_STATE = os.path.join(ROOT, "config", "indexnow_redirects.json")
KEYFILE = os.path.join(ROOT, ".indexnow-key")
# Any participating engine shares the submission with all the others, so a second endpoint is a
# fallback for network failures only (the daily job has hit DNS errors on api.indexnow.org).
ENDPOINTS = ("https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow",
             "https://yandex.com/indexnow")
UA = "Consulting24-IndexNow/1.0 (+https://www.consulting24.co/)"
STUB_MARK = "generated-redirect-stub"


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=0)


def key():
    with open(KEYFILE, encoding="utf-8") as f:
        return f.read().strip()


def enqueue(urls):
    """Append URLs to the queue (dedupe, keep order). Returns the new queue length."""
    urls = [u for u in urls if u.startswith(BASE + "/")]
    queue = list(dict.fromkeys(_load(QUEUE, []) + urls))
    _save(QUEUE, queue)
    return len(queue)


def redirect_delta():
    """Legacy URLs from config/redirects.json whose stub is new or re-pointed since the last build.
    The FAQ asks for redirected URLs to be submitted too; each one goes out once, not daily."""
    cur = _load(REDIRECTS, {}).get("redirects", {})
    seen = _load(REDIRECT_STATE, {})
    delta = [BASE + src for src, dst in sorted(cur.items()) if seen.get(src) != dst]
    _save(REDIRECT_STATE, dict(sorted(cur.items())))
    return delta


# ---- live check ------------------------------------------------------------------------------
def _fetch(url):
    """(status, html). Follows redirects the way a crawler does; network trouble -> (None, '')."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def live_ready(url, hashes, redirect_urls):
    """True when the live site already serves the version we are about to announce."""
    status, html = _fetch(url)
    if status is None:
        return False
    if url in hashes:                                        # a live page: new content deployed?
        return status == 200 and content_digest(html) == hashes[url]["hash"]
    if url in redirect_urls:                                 # a legacy URL: stub deployed?
        return status == 200 and STUB_MARK in html
    # removed from the build: gone, or replaced by a stub / noindex page
    return status in (404, 410) or (status == 200 and (STUB_MARK in html or 'content="noindex' in html))


# ---- submission --------------------------------------------------------------------------------
def submit(urls):
    """POST one batch (spec: <=10,000 URLs, same host). Returns (ok, message).
    200 = accepted, 202 = accepted with key validation pending. 400/403/422/429 are not retried on
    another endpoint: they are our problem (format, key, host) or a rate limit, and every engine
    would answer the same."""
    k = key()
    body = json.dumps({"host": HOST, "key": k, "keyLocation": f"{BASE}/{k}.txt",
                       "urlList": urls}).encode("utf-8")
    last = "no endpoint tried"
    for ep in ENDPOINTS:
        req = urllib.request.Request(ep, data=body, method="POST", headers={
            "Content-Type": "application/json; charset=utf-8", "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                note = " (key validation pending)" if r.status == 202 else ""
                return True, f"HTTP {r.status}{note} from {ep}"
        except urllib.error.HTTPError as e:
            detail = e.read(300).decode("utf-8", "ignore").strip()
            if e.code == 429:
                return False, f"HTTP 429 rate-limited by {ep} (Retry-After: {e.headers.get('Retry-After')})"
            if e.code < 500:
                return False, f"HTTP {e.code} from {ep}: {detail or e.reason}"
            last = f"HTTP {e.code} from {ep}"
        except Exception as e:
            last = f"{ep}: {e}"
    return False, f"all endpoints failed, last: {last}"


def flush(wait=0, dry_run=False):
    queue = _load(QUEUE, [])
    log = _load(LOG, {})
    today = datetime.date.today().isoformat()
    room = CAP - len(log.get(today, []))
    if not queue:
        print("IndexNow flush: queue empty")
        return 0
    if room <= 0:
        print(f"IndexNow flush: daily cap {CAP} reached, {len(queue)} stay queued")
        return 0
    if not os.path.exists(KEYFILE):
        print("IndexNow flush: no .indexnow-key, queue kept")
        return 0

    hashes = _load(HASHES, {})
    redirect_urls = {BASE + s for s in _load(REDIRECTS, {}).get("redirects", {})}
    pending, ready = list(queue), []
    deadline = time.time() + wait
    while True:
        with ThreadPoolExecutor(8) as ex:
            ok = list(ex.map(lambda u: live_ready(u, hashes, redirect_urls), pending))
        ready += [u for u, r in zip(pending, ok) if r]
        pending = [u for u, r in zip(pending, ok) if not r]
        if not pending or len(ready) >= room or time.time() >= deadline:
            break
        print(f"IndexNow flush: {len(pending)} not live yet, re-checking in 30s")
        time.sleep(30)

    batch = ready[:room]
    if batch and dry_run:
        print(f"IndexNow flush (dry run): would submit {len(batch)}: {', '.join(batch[:5])}"
              f"{' ...' if len(batch) > 5 else ''}")
    elif batch:
        ok, msg = submit(batch)
        print(f"IndexNow: {msg} for {len(batch)} URLs")
        if ok:
            sent = set(batch)
            queue = [u for u in queue if u not in sent]
            log.setdefault(today, []).extend(batch)
            cutoff = (datetime.date.today() - datetime.timedelta(days=60)).isoformat()
            log = {d: v for d, v in log.items() if d >= cutoff}   # keep ~60 days
            _save(QUEUE, queue)
            _save(LOG, log)
    if pending:
        print(f"IndexNow flush: {len(pending)} queued URLs not live in the new version yet "
              f"(stay queued): {', '.join(pending[:5])}{' ...' if len(pending) > 5 else ''}")
    return len(batch)


def status():
    queue, log = _load(QUEUE, []), _load(LOG, {})
    today = datetime.date.today().isoformat()
    print(f"queue {len(queue)}, submitted today {len(log.get(today, []))}/{CAP}")
    if os.path.exists(KEYFILE):
        k = key()
        st, body = _fetch(f"{BASE}/{k}.txt")
        print(f"key file {BASE}/{k}.txt -> HTTP {st}, matches: {body.strip() == k}")


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "status"
    if cmd == "flush":
        flush(int(args[args.index("--wait") + 1]) if "--wait" in args else 0, "--dry-run" in args)
    elif cmd == "add":
        print(f"queued, queue now {enqueue(args[1:])}")
    else:
        status()
