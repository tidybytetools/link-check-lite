import io, os, sys, tempfile, threading, unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import link_check_lite as lite


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, loc=None):
        self.send_response(code)
        if loc: self.send_header("Location", loc)
        self.send_header("Content-Length", "2"); self.end_headers()
        if self.command == "GET": self.wfile.write(b"hi")
    def route(self):
        p = self.path
        if p == "/ok": return self._send(200)
        if p == "/a": return self._send(301, "/b")
        if p == "/b": return self._send(302, "/ok")
        if p == "/loop": return self._send(302, "/loop")
        if p == "/nohead": return self._send(405 if self.command == "HEAD" else 200)
        return self._send(404)
    do_GET = do_HEAD = route


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.b = f"http://127.0.0.1:{cls.srv.server_port}"
    @classmethod
    def tearDownClass(cls): cls.srv.shutdown(); cls.srv.server_close()

    def test_ok(self):
        r = lite.check_link(self.b + "/ok")
        self.assertEqual((r["status"], r["ok"], r["redirects"]), (200, True, []))
    def test_404(self):
        r = lite.check_link(self.b + "/gone")
        self.assertEqual((r["status"], r["ok"]), (404, False))
    def test_redirects(self):
        r = lite.check_link(self.b + "/a")
        self.assertEqual(r["final_url"], self.b + "/ok"); self.assertEqual(len(r["redirects"]), 2)
        self.assertTrue(r["redirects"][0].startswith("301 ")); self.assertTrue(r["ok"])
    def test_loop(self):
        r = lite.check_link(self.b + "/loop")
        self.assertEqual(r["error"], "redirect loop"); self.assertFalse(r["ok"])
    def test_head_refused(self):
        self.assertEqual(lite.check_link(self.b + "/nohead")["status"], 200)
    def test_cannot_connect(self):
        r = lite.check_link("http://127.0.0.1:1/x", timeout=2)
        self.assertIsNone(r["status"]); self.assertTrue(r["error"])
    def test_not_http(self):
        self.assertEqual(lite.check_link("mailto:a@b.c")["error"], "not an http(s) link")
    def test_cli(self):
        d = tempfile.mkdtemp(); p = os.path.join(d, "l.txt")
        with open(p, "w") as f: f.write(f"# list\n{self.b}/ok\n{self.b}/a\n{self.b}/ok\n")
        self.assertEqual(lite.read_links(p), [self.b + "/ok", self.b + "/a"])
        buf = io.StringIO()
        with redirect_stdout(buf): code = lite.main([p])
        self.assertEqual(code, 0); self.assertIn("2 checked, 2 ok, 0 broken", buf.getvalue())
        self.assertNotIn("gumroad", buf.getvalue())  # no upsell when not a terminal
        with open(p, "a") as f: f.write(f"{self.b}/gone\n")
        with redirect_stdout(io.StringIO()): self.assertEqual(lite.main([p]), 1)


if __name__ == "__main__":
    unittest.main()
