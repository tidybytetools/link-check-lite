# link-check-lite

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP server](https://img.shields.io/badge/MCP-stdio-purple.svg)](#use-it-from-claude-desktop-or-cursor-mcp)

Free tool that checks a list of links. It tells you which ones work, which are broken, and where redirects end up.
Need sitemaps, speed checks, sketchy-domain warnings or CSV reports? The paid version does that: **[link-check on Gumroad](https://tidybyte.gumroad.com/l/LINK_CHECK_PAID_URL)**

MIT license. Python 3.10 or newer, on Windows, Mac and Linux. The checker itself uses only Python's built-in tools.

## Install

```
pip install git+https://github.com/tidybytetools/link-check-lite
```

## Use it

Put your links in a text file, one per line. Lines that start with `#` are skipped.

```
link-check-lite links.txt
link-check-lite links.txt -w 3 --timeout 20   # gentler and more patient
```

Example run:

```
OK   200 https://example.com/
OK   200 https://httpbin.org/redirect/2  -> https://httpbin.org/get (2 redirects)
FAIL 404 https://example.com/old-page
FAIL --- https://no-such-site.example  ([Errno -2] Name or service not known)

4 checked, 2 ok, 2 broken
```

Exit code is 0 when every link works and 1 when any link is broken, so it works in a cron job or CI.

When you run it in a terminal it ends with one short line about the paid version. `--quiet` turns it off, and it never shows when output is piped.

## Known limits

- **Some sites block bots.** They may answer 403 or 429 even when the page opens fine in a browser.
- **No JavaScript.** Redirects done with JavaScript are not followed.
- **Text file only.** No CSV input, no sitemaps, and results print to the screen.
- **No robots.txt and no per-site rate limit.** It checks 5 links at a time with a small pause. Don't point it at thousands of pages on one site.
- **Not a safety check.** It does not tell you if a link is a scam.

## Lite vs paid

| | lite (free) | [link-check](https://tidybyte.gumroad.com/l/LINK_CHECK_PAID_URL) |
|---|---|---|
| Status codes and broken links | yes | yes |
| Redirect chain and final URL | yes | yes |
| Text file input | yes | yes |
| CSV input and sitemap URLs (with sitemap index) | no | yes |
| Response time and slow-link flag | no | yes |
| http vs https checks | no | yes |
| Look-alike and sketchy domain warnings (local rules) | no | yes |
| robots.txt and one-hit-per-second per site | no | yes |
| CSV, JSON and Markdown reports | no | yes |

## How it compares to other free tools

All of these are free. Pick what fits you.

| | link-check-lite | [lychee](https://github.com/lycheeverse/lychee) | [linkchecker](https://github.com/linkchecker/linkchecker) | [muffet](https://github.com/raviqqe/muffet) |
|---|---|---|---|---|
| Checks a plain list of links | yes | yes | no, it crawls | no, it crawls |
| Crawls a whole site | no | no | yes | yes |
| Install | pip | binary / cargo | pip | binary / go |
| Built-in MCP server for AI apps | yes | no | no | no |
| Lots of options | no | yes | yes | yes |

If you need to crawl a big site or check links inside Markdown files, lychee and linkchecker are great.

## Use it from Claude Desktop or Cursor (MCP)

There is a small free MCP server built in. It gives your AI app one tool, `check_links`. It needs [uv](https://docs.astral.sh/uv/).

```
uvx --from git+https://github.com/tidybytetools/link-check-lite link-check-lite-mcp
```

Claude Desktop (`claude_desktop_config.json`) or Cursor (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "link-check-lite": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/tidybytetools/link-check-lite", "link-check-lite-mcp"]
    }
  }
}
```

Tool: `check_links(urls, timeout=10.0)`. Send up to 200 links. It returns one result per link.

## Use it from Python

```python
from link_check_lite import check_link
print(check_link("https://example.com"))
# {'url': 'https://example.com', 'status': 200, 'ok': True, 'final_url': 'https://example.com', 'redirects': [], 'error': None}
```

## For AI agents

- **Use when:** you need to know if web links work and where their redirects end up.
- **Don't use when:** you need to know if a link is safe, need a whole site crawled, or need speed or https checks. Use the paid version for those.
- **Input:** a list of http(s) URLs (max 200 per MCP call), plus an optional `timeout` in seconds.
- **Output:** a list of `{url, status, ok, final_url, redirects, error}`. `status` is null when the link could not connect. `ok` is true for 200-399. `redirects` lists each hop as `"CODE url"`.
- CLI exit code is 0 when all links work and 1 when any link is broken or on error. See also [`llms.txt`](llms.txt).

## Tests

```
pip install "mcp>=1.2,<2"
python3 -m unittest discover tests
```

The tests use a tiny local web server, so they don't need the internet.

## License

MIT. See `LICENSE`.
