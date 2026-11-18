#!/usr/bin/env python3
"""link-check-lite: check a file of links for status codes and redirects.

Free and MIT licensed. Paid version (sitemaps, CSV input, speed, https checks,
odd-domain warnings, robots.txt, CSV/JSON/Markdown reports):
https://tidybyte.gumroad.com/l/link-check

Need thousands of URLs on a schedule, or no install? Use our hosted HTTP
Status Checker on Apify:
https://apify.com/store?search=tidybytetools%20http%20status
"""
import argparse, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

__version__ = "1.2.0"
PAID_URL = "https://tidybyte.gumroad.com/l/link-check"
APIFY_STATUS_URL = "https://apify.com/store?search=tidybytetools%20http%20status"
UA = "link-check-lite/1.2 (+https://github.com/tidybytetools/link-check-lite)"
MAX_HOPS = 10
MAX_WORKERS = 10


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
    """Check one link. Returns {url, status, ok, final_url, redirects, error, ms}.

    redirects is a list of "CODE url" hops. ok is True for a final status 200-399.
    ms is how long the check took, in milliseconds.
    """
    t0 = time.perf_counter()
    hops, cur, seen, err, code = [], url, set(), None, None
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        return {
            "url": url,
            "status": None,
            "ok": False,
            "final_url": url,
            "redirects": [],
            "error": "not an http(s) link",
            "ms": int(round((time.perf_counter() - t0) * 1000)),
        }
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
    return {
        "url": url,
        "status": code,
        "ok": ok,
        "final_url": cur,
        "redirects": hops,
        "error": err,
        "ms": int(round((time.perf_counter() - t0) * 1000)),
    }


def read_links_from_lines(lines):
    out = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and line not in out:
            out.append(line if "://" in line else "https://" + line)
    return out


def read_links(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return read_links_from_lines(f)


def clamp_workers(workers):
    """Keep concurrency polite: at least 1, at most MAX_WORKERS (10)."""
    try:
        n = int(workers)
    except (TypeError, ValueError):
        n = 5
    return max(1, min(n, MAX_WORKERS))


def check_links(urls, workers=5, timeout=10.0, delay=0.5):
    """Check many links, a few at a time, with a short pause between starts."""
    workers = clamp_workers(workers)
    def job(i_url):
        i, u = i_url
        time.sleep(i * delay / max(workers, 1))
        return check_link(u, timeout)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(job, enumerate(urls)))


def format_status_line(r):
    """One status-mode line: code, time, URL, and redirect target if it moved.

    When the URL redirected, the code is the first hop (for example 301) and the
    final URL is shown after ->. The final status is added in parentheses when it
    differs from the first hop.
    """
    if r["redirects"]:
        code = r["redirects"][0].split()[0]
    else:
        code = r["status"] if r["status"] is not None else "---"
    line = f"{code:>3}  {r['ms']:>5}ms  {r['url']}"
    if r["final_url"] and r["final_url"] != r["url"]:
        line += f"  -> {r['final_url']}"
        if r["status"] is not None and str(r["status"]) != str(code):
            line += f" ({r['status']})"
    if r["error"]:
        line += f"  ({r['error']})"
    return line


def run_mcp():
    """Start the stdio MCP server (needs the mcp package, which pip installs for you)."""
    try:
        import link_check_lite_mcp
    except ImportError as e:
        print(f"error: the MCP server needs the mcp package ({e}). Run: pip install link-check-lite", file=sys.stderr)
        return 1
    link_check_lite_mcp.main()
    return 0


def _load_urls(path):
    if path == "-":
        return read_links_from_lines(sys.stdin)
    return read_links(path)


def run_status(argv):
    """CLI for `link-check-lite status`: print status, redirect target and time."""
    ap = argparse.ArgumentParser(
        prog="link-check-lite status",
        description="Check a list of URLs and print each status code, redirect target and response time.",
    )
    ap.add_argument(
        "file",
        nargs="?",
        default=None,
        help="text file, one URL per line (# lines are skipped). Use - or omit the file to read from stdin.",
    )
    ap.add_argument("-w", "--workers", type=int, default=5, help="links at the same time (default 5, max 10)")
    ap.add_argument("--timeout", type=float, default=10, help="seconds per link (default 10)")
    ap.add_argument("-q", "--quiet", action="store_true", help="hide the one-line note about the hosted checker")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    path = a.file
    if path is None:
        if sys.stdin.isatty():
            print("error: pass a file of URLs, or pipe them in (one per line)", file=sys.stderr)
            return 1
        path = "-"
    try:
        urls = _load_urls(path)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if not urls:
        print("error: no links found", file=sys.stderr)
        return 1
    rows = check_links(urls, a.workers, a.timeout)
    failed = 0
    for r in rows:
        print(format_status_line(r))
        if r["status"] is None:
            failed += 1
    print(f"\n{len(rows)} checked")
    if not a.quiet and sys.stdout.isatty():
        print(
            "Need thousands of URLs on a schedule, or no install? "
            f"Use our hosted HTTP Status Checker on Apify: {APIFY_STATUS_URL}"
        )
    return 1 if failed else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["mcp"]:
        return run_mcp()
    if argv and argv[0] == "status":
        return run_status(argv[1:])
    ap = argparse.ArgumentParser(
        prog="link-check-lite",
        description="Check a file of links for status codes and redirects.",
        epilog="For a status-and-timing report (file or stdin): link-check-lite status [file]. "
        "For the MCP server: link-check-lite mcp. To check a file named status or mcp, pass ./status or ./mcp.",
    )
    ap.add_argument("file", help="text file, one link per line (# lines are skipped)")
    ap.add_argument("-w", "--workers", type=int, default=5, help="links at the same time (default 5, max 10)")
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
