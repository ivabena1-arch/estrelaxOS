from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import sqlite3,json,os
os.chdir(Path(__file__).resolve().parent)
def db():
    c=sqlite3.connect('forum.db'); c.execute('CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY, author TEXT, title TEXT, body TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP)'); return c
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(Path('public').resolve()),**kwargs)
    def reply(self,data,status=200):
        b=json.dumps(data,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path=='/api/posts':
            with db() as c:
                c.row_factory=sqlite3.Row; self.reply([dict(r) for r in c.execute('SELECT * FROM posts ORDER BY id DESC LIMIT 100')]); return
        super().do_GET()
    def do_POST(self):
        if self.path!='/api/posts': return self.reply({'error':'Ruta inexistente'},404)
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<=24000: raise ValueError()
            d=json.loads(self.rfile.read(n)); values=[d[k].strip() for k in ('author','title','body')]
            if not all(0<len(v)<=m for v,m in zip(values,(60,120,4000))): raise ValueError()
        except (ValueError,KeyError,TypeError,AttributeError): return self.reply({'error':'Publicación inválida'},400)
        with db() as c: c.execute('INSERT INTO posts(author,title,body) VALUES(?,?,?)',values)
        self.reply({'ok':True},201)
if __name__=='__main__':
    with db(): pass
    print('http://localhost:9090',flush=True); ThreadingHTTPServer(('127.0.0.1',9090),Handler).serve_forever()
