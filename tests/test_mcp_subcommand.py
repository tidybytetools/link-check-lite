"""`link-check-lite mcp` starts the MCP server (this is how the MCP Registry launches it)."""
import asyncio, os, subprocess, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    ClientSession = None

ANN = {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}


async def _tools():
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(ROOT, "link_check_lite.py"), "mcp"], cwd=ROOT)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            return (await s.list_tools()).tools


@unittest.skipIf(ClientSession is None, "mcp not installed")
class McpSubcommand(unittest.TestCase):
    def test_mcp_subcommand_lists_tool_with_annotations(self):
        tools = asyncio.run(_tools())
        self.assertEqual([t.name for t in tools], ["check_links"])
        ann = tools[0].annotations
        self.assertIsNotNone(ann)
        for k, v in ANN.items():
            self.assertIs(getattr(ann, k), v, k)


class CliStillWorks(unittest.TestCase):
    def test_version_and_help(self):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "link_check_lite.py"), "--version"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout.strip(), "1.1.4")
        h = subprocess.run([sys.executable, os.path.join(ROOT, "link_check_lite.py"), "--help"], capture_output=True, text=True)
        self.assertEqual(h.returncode, 0)


if __name__ == "__main__":
    unittest.main()
