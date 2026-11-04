# Changelog

What changed in link-check-lite, newest first.

## 1.1.0 - 2026-11-04

- MCP tool now has safety labels (tool annotations) so AI apps know what it does:
  readOnlyHint true, destructiveHint false, idempotentHint true, openWorldHint true.
- The tool description now says when to use it and when not to.
- Needs mcp 1.10 or newer.

## 1.0.0 - 2026-11-04

- First release.
- Checks a text file of links and shows status codes, broken links and where redirects end up.
- Exit code 1 when any link is broken, so it works in cron jobs and CI.
- Free MCP server, `link-check-lite-mcp`, with one tool, `check_links`.
- You can install it from PyPI with `pip install link-check-lite`.
