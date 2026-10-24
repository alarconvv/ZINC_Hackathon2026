"""Local static Expo export server, including extensionless route URLs."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / 'dist'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if not Path(str(ROOT) + path).is_file() and Path(str(ROOT) + path + '.html').is_file():
            self.path = path + '.html'
        super().do_GET()
    def log_message(self, *args):
        pass
ThreadingHTTPServer(('127.0.0.1', 8081), Handler).serve_forever()
