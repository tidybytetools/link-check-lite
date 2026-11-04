"""Free MCP server for link-check-lite (stdio).

Run:  uvx --from git+https://github.com/tidybytetools/link-check-lite link-check-lite-mcp
"""
from mcp.server.fastmcp import FastMCP
import link_check_lite as lite

mcp = FastMCP("link-check-lite")


@mcp.tool()
def check_links(urls: list[str], timeout: float = 10.0) -> list[dict]:
    """Check web links and follow their redirects.

    urls: up to 200 http(s) links.
    timeout: seconds to wait for each link.

    Returns one result per link: {url, status, ok, final_url, redirects, error}.
    status is the HTTP code of the last hop (null if it could not connect).
    ok is true for 200-399. redirects lists each hop as "CODE url".
    """
    if len(urls) > 200:
        raise ValueError("send 200 links or fewer per call")
    return lite.check_links(list(urls), workers=5, timeout=timeout)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
