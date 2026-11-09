#!/usr/bin/env python3
"""link-check-lite: check a file of links for status codes and redirects.

Free and MIT licensed. Paid version (sitemaps, CSV input, speed, https checks,
odd-domain warnings, robots.txt, CSV/JSON/Markdown reports):
https://tidybyte.gumroad.com/l/link-check
"""
import argparse, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

__version__ = "1.1.4"
PAID_URL = "https://tidybyte.gumroad.com/l/link-check"
UA = "link-check-lite/1.0 (+https://github.com/tidybytetools/link-check-lite)"
MAX_HOPS = 10


class _Stop(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_opener = urllib.request.build_opener(_Stop)


def _hit(url, method, timeout):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    try:
        with _opener.open(req, timeout=timeout) as r:
            return r.status, r.headers.get("Location"), None
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location"), None
    except urllib.error.URLError as e:
        return None, None, str(e.reason)
    except Exception as e:  # timeouts and odd errors
        return None, None, str(e) or e.__class__.__name__


def check_link(url, timeout=10.0):
    """Check one link. Returns {url, status, ok, final_url, redirects, error}.

    redirects is a list of "CODE url" hops. ok is True for a final status 200-399.
    """
    hops, cur, seen, err, code = [], url, set(), None, None
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        return {"url": url, "status": None, "ok": False, "final_url": url, "redirects": [], "error": "not an http(s) link"}
    for _ in range(MAX_HOPS + 1):
        code, loc, err = _hit(cur, "HEAD", timeout)
        if code in (403, 405, 501):
            code, loc, err = _hit(cur, "GET", timeout)  # some servers refuse HEAD
        if err or code not in (301, 302, 303, 307, 308) or not loc:
            break
        hops.append(f"{code} {cur}")
        seen.add(cur)
        cur = urllib.parse.urljoin(cur, loc)
        if cur in seen:
            err = "redirect loop"
            break
    else:
        err = f"more than {MAX_HOPS} redirects"
    ok = err is None and code is not None and 200 <= code < 400
    return {"url": url, "status": code, "ok": ok, "final_url": cur, "redirects": hops, "error": err}


def read_links(path):
    out = []
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and line not in out:
                out.append(line if "://" in line else "https://" + line)
    return out


def check_links(urls, workers=5, timeout=10.0, delay=0.5):
    """Check many links, a few at a time, with a short pause between starts."""
    def job(i_url):
        i, u = i_url
        time.sleep(i * delay / max(workers, 1))
        return check_link(u, timeout)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        return list(ex.map(job, enumerate(urls)))


def run_mcp():
    """Start the stdio MCP server (needs the mcp package, which pip installs for you)."""
    try:
        import link_check_lite_mcp
    except ImportError as e:
        print(f"error: the MCP server needs the mcp package ({e}). Run: pip install link-check-lite", file=sys.stderr)
        return 1
    link_check_lite_mcp.main()
    return 0

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["mcp"]:
        return run_mcp()
    ap = argparse.ArgumentParser(prog="link-check-lite", description="Check a file of links for status codes and redirects.")
    ap.add_argument("file", help="text file, one link per line (# lines are skipped)")
    ap.add_argument("-w", "--workers", type=int, default=5, help="links at the same time (default 5)")
    ap.add_argument("--timeout", type=float, default=10, help="seconds per link (default 10)")
    ap.add_argument("-q", "--quiet", action="store_true", help="hide the one-line note about the paid version")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    try:
        urls = read_links(a.file)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if not urls:
        print("error: no links found", file=sys.stderr)
        return 1
    rows = check_links(urls, a.workers, a.timeout)
    bad = 0
    for r in rows:
        mark = "OK  " if r["ok"] else "FAIL"
        bad += not r["ok"]
        line = f"{mark} {r['status'] or '---'} {r['url']}"
        if r["redirects"]:
            line += f"  -> {r['final_url']} ({len(r['redirects'])} redirect{'s' * (len(r['redirects']) > 1)})"
        if r["error"]:
            line += f"  ({r['error']})"
        print(line)
    print(f"\n{len(rows)} checked, {len(rows) - bad} ok, {bad} broken")
    if not a.quiet and sys.stdout.isatty():
        print(f"Need sitemaps, CSV/JSON reports, speed and sketchy-domain checks? {PAID_URL}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
