# Changelog

What changed in link-check-lite, newest first.

## 1.1.4 - 2026-11-09

- Point Homepage, Documentation, and the MCP Registry websiteUrl at the official product page on [tidybytetools.github.io](https://tidybytetools.github.io/tools/link-check/).
- README: add a clear Links section (Website, Apify cloud version where it exists, Pro on Gumroad) and a short FAQ.

## 1.1.3 - 2026-11-09

- The Python package, the MCP Registry entry and the GitHub Action now all use version 1.1.3. The v1.1.2 GitHub release did not publish to PyPI, because the package version was still 1.1.1.

## Action v1.1.2 - 2026-11-04

- New: a GitHub Action (`action.yml`), now on the GitHub Marketplace. Add `uses: tidybytetools/link-check-lite@v1` to a workflow to check a links file on every push.
- This release only added the action. The Python package stays at 1.1.1 on PyPI.

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
