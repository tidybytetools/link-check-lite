# Changelog

What changed in link-check-lite, newest first.

## Unreleased

- New: a GitHub Action (`action.yml`). Add `uses: tidybytetools/link-check-lite@main` to a workflow to check a links file on every push.

## 1.1.1 - 2026-11-04

- Fix: installing from the MCP Registry now starts the MCP server. Before, it started the plain command-line tool by mistake.
- New: `link-check-lite mcp` starts the MCP server. `uvx link-check-lite mcp` works too. The old `link-check-lite-mcp` command still works.
- To read a file that is named `mcp`, use `./mcp`.

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
