"""Free MCP server for link-check-lite (stdio).

Run:  uvx --from git+https://github.com/tidybytetools/link-check-lite link-check-lite-mcp
"""
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
import link_check_lite as lite

mcp = FastMCP("link-check-lite")


@mcp.tool(
    title="Check links",
    annotations=ToolAnnotations(
        title="Check links",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def check_links(urls: list[str], timeout: float = 10.0) -> list[dict]:
    """Check web links and follow their redirects.

    Use this when you have a list of URLs and need to know which ones work, which
    are broken (404, 500, timeouts, bad hosts) and where redirects end up, for
    example to clean up docs, a README, a sitemap list or bookmarks. It does not
    crawl a site or read page content; pass the exact links you want checked.
    Links that are not http or https come back with ok false and an error.

    urls: up to 200 http(s) links.
    timeout: seconds to wait for each link.

    Returns one result per link: {url, status, ok, final_url, redirects, error, ms}.
    status is the HTTP code of the last hop (null if it could not connect).
    ok is true for 200-399. redirects lists each hop as "CODE url".
    ms is how long the check took, in milliseconds.
    """
    if len(urls) > 200:
        raise ValueError("send 200 links or fewer per call")
    return lite.check_links(list(urls), workers=5, timeout=timeout)


@mcp.tool(
    title="Check URL status",
    annotations=ToolAnnotations(
        title="Check URL status",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def check_status(urls: list[str], timeout: float = 10.0) -> list[dict]:
    """Check the HTTP status code, redirect target and response time of each URL.

    Use this when you need a compact status report: the status code, where a
    redirect ends, and how many milliseconds each URL took. It does not crawl a
    site or read page content; pass the exact links you want checked. Links that
    are not http or https come back with ok false and an error. Checks run a few
    at a time (at most 10) with a short pause, so they stay polite.

    urls: up to 200 http(s) links.
    timeout: seconds to wait for each link.

    Returns one result per link: {url, status, ok, final_url, redirects, error, ms}.
    status is the HTTP code of the last hop (null if it could not connect).
    final_url is the redirect target (the same as url when it did not move).
    ms is how long the check took, in milliseconds.
    """
    if len(urls) > 200:
        raise ValueError("send 200 links or fewer per call")
    return lite.check_links(list(urls), workers=5, timeout=timeout)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
