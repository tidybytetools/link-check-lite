import asyncio, os, sys, threading, unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from test_lite import H
try:
    import mcp  # noqa
except ImportError:
    mcp = None

ROOT = os.path.join(os.path.dirname(__file__), "..")


@unittest.skipIf(mcp is None, 'pip install "mcp>=1.2,<2" to run this test')
class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.b = f"http://127.0.0.1:{cls.srv.server_port}"
    @classmethod
    def tearDownClass(cls): cls.srv.shutdown(); cls.srv.server_close()

    def test_stdio_roundtrip(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        import json

        async def go():
            params = StdioServerParameters(command=sys.executable, args=[os.path.join(ROOT, "link_check_lite_mcp.py")], cwd=ROOT)
            async with stdio_client(params) as (r, w):
                async with ClientSession(r, w) as s:
                    await s.initialize()
                    tools = await s.list_tools()
                    self.assertEqual([t.name for t in tools.tools], ["check_links"])
                    res = await s.call_tool("check_links", {"urls": [self.b + "/a", self.b + "/gone"]})
                    self.assertFalse(res.isError)
                    data = res.structuredContent["result"] if res.structuredContent else [json.loads(c.text) for c in res.content]
                    return data
        data = asyncio.run(go())
        self.assertEqual(data[0]["final_url"], self.b + "/ok")
        self.assertEqual(data[1]["status"], 404)


if __name__ == "__main__":
    unittest.main()
