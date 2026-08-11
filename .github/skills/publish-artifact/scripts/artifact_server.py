#!/usr/bin/env python3
"""Serve agent artifacts with a responsive management homepage."""

from __future__ import annotations

import argparse
import datetime as dt
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
import os
from pathlib import Path
import secrets
import shutil
from urllib.parse import quote, urlsplit

DEFAULT_ROOT = Path.home() / ".local" / "share" / "agent-artifacts" / "public"
API_PREFIX = "/__api/artifacts"
MAX_REQUEST_BYTES = 16 * 1024

DASHBOARD_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b1020">
<title>Agent Artifacts</title>
<style>
:root{color-scheme:dark;--bg:#0b1020;--panel:#141b2d;--panel2:#1b253a;--line:#2c3953;--text:#f5f7fb;--muted:#9cabc3;--cyan:#64d8e8;--green:#62d99f;--red:#ff7d8d;--shadow:0 18px 50px #0007}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 10% 0,#17294a 0,transparent 35rem),var(--bg);color:var(--text);font:14px/1.4 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}button,input{font:inherit}button{cursor:pointer}.shell{width:min(1280px,100%);margin:auto;padding:max(17px,env(safe-area-inset-top)) max(14px,env(safe-area-inset-right)) max(28px,env(safe-area-inset-bottom)) max(14px,env(safe-area-inset-left))}header{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin:4px 0 17px}.eyebrow{color:var(--cyan);font-size:10px;font-weight:800;letter-spacing:.15em;text-transform:uppercase}h1{font-size:clamp(26px,4vw,39px);line-height:1.05;margin:5px 0 6px;letter-spacing:-.035em}.subtitle{margin:0;color:var(--muted);max-width:720px;font-size:13px}.refresh{border:1px solid var(--line);background:#182238;color:var(--text);border-radius:10px;padding:7px 10px;white-space:nowrap}.refresh:hover{border-color:var(--cyan)}.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 12px}.search{position:relative;flex:1 1 260px}.search input{width:100%;border:1px solid var(--line);background:#11192b;color:var(--text);border-radius:11px;padding:9px 12px 9px 35px;outline:none}.search input:focus{border-color:var(--cyan);box-shadow:0 0 0 3px #64d8e822}.search:before{content:"⌕";position:absolute;left:12px;top:4px;font-size:21px;color:var(--muted)}.filters{display:flex;gap:5px;overflow:auto;padding:1px}.filter{border:1px solid var(--line);background:#11192b;color:var(--muted);border-radius:999px;padding:6px 10px}.filter.active{background:var(--cyan);border-color:var(--cyan);color:#07131b;font-weight:800}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}.card{display:flex;flex-direction:column;min-height:168px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(145deg,var(--panel2),var(--panel));padding:13px;box-shadow:0 6px 20px #0003}.card:hover{border-color:#435776;transform:translateY(-1px)}.card-top{display:flex;justify-content:space-between;gap:9px}.icon{display:grid;place-items:center;width:35px;height:35px;border-radius:10px;background:#24324b;font-size:10px;font-weight:900;letter-spacing:.04em}.badge{align-self:flex-start;border-radius:999px;padding:4px 7px;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.05em;background:#25334c;color:var(--muted)}.badge.live{background:#123a31;color:var(--green)}.badge.broken{background:#4a252d;color:var(--red)}.card h2{font-size:15px;line-height:1.2;margin:10px 0 4px;overflow-wrap:anywhere}.meta{color:var(--muted);font-size:11px;margin-bottom:10px}.actions{display:flex;gap:6px;margin-top:auto}.action{border:1px solid var(--line);background:#101827;color:var(--text);border-radius:8px;padding:7px 9px;text-decoration:none;text-align:center;min-width:58px}.action.primary{background:var(--cyan);border-color:var(--cyan);color:#07131b;font-weight:800;flex:1}.action.delete{color:var(--red)}.action:hover{filter:brightness(1.12)}.empty{grid-column:1/-1;text-align:center;border:1px dashed var(--line);border-radius:14px;padding:42px 16px;color:var(--muted)}.empty strong{display:block;color:var(--text);font-size:17px;margin-bottom:5px}.toast{position:fixed;right:16px;bottom:16px;max-width:min(360px,calc(100vw - 32px));padding:10px 13px;border-radius:10px;background:#eafcff;color:#07131b;box-shadow:var(--shadow);opacity:0;transform:translateY(12px);pointer-events:none;transition:.2s}.toast.show{opacity:1;transform:none}.loading{animation:pulse 1.2s infinite alternate}@keyframes pulse{to{opacity:.45}}@media(max-width:620px){header{align-items:stretch;flex-direction:column;gap:10px;margin-bottom:14px}.refresh{align-self:flex-start}.grid{grid-template-columns:1fr}.shell{padding-left:11px;padding-right:11px}.toolbar{margin-bottom:10px}}
</style>
</head>
<body>
<main class="shell">
<header><div><div class="eyebrow">LAN / VPN library</div><h1>Agent Artifacts</h1><p class="subtitle">Open, copy, and manage output published by your agent sessions. Live items track their original files; snapshots stay unchanged.</p></div><button class="refresh" id="refresh">↻ Refresh</button></header>
<section class="toolbar"><label class="search"><input id="search" type="search" placeholder="Search artifacts…" autocomplete="off"></label><div class="filters" id="filters"><button class="filter active" data-filter="all">All</button><button class="filter" data-filter="snapshot">Snapshots</button><button class="filter" data-filter="live">Live</button><button class="filter" data-filter="broken">Broken</button></div></section>
<section class="grid" id="grid"><div class="empty loading"><strong>Loading artifacts…</strong></div></section>
</main><div class="toast" id="toast" role="status"></div>
<script>
const csrf=__CSRF_TOKEN__;let artifacts=[],filter='all';const $=s=>document.querySelector(s);const grid=$('#grid');
const fmtSize=n=>n==null?'size varies':n<1024?n+' B':n<1048576?(n/1024).toFixed(1)+' KB':n<1073741824?(n/1048576).toFixed(1)+' MB':(n/1073741824).toFixed(1)+' GB';
const fmtTime=s=>new Intl.DateTimeFormat(undefined,{dateStyle:'medium',timeStyle:'short'}).format(new Date(s));
function toast(message){const el=$('#toast');el.textContent=message;el.classList.add('show');clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('show'),2400)}
function button(label,kind,fn){const b=document.createElement('button');b.className='action '+(kind||'');b.textContent=label;b.addEventListener('click',fn);return b}
async function copyUrl(url){try{await navigator.clipboard.writeText(url)}catch{const i=document.createElement('input');i.value=url;document.body.append(i);i.select();document.execCommand('copy');i.remove()}toast('URL copied')}
function render(){const query=$('#search').value.trim().toLowerCase();const shown=artifacts.filter(a=>(filter==='all'||a.mode===filter||(filter==='broken'&&a.broken))&&(!query||a.title.toLowerCase().includes(query)||a.name.toLowerCase().includes(query)));grid.replaceChildren();if(!shown.length){const e=document.createElement('div');e.className='empty';e.innerHTML='<strong>No matching artifacts</strong>Try another filter or publish a new file.';grid.append(e);return}for(const a of shown){const card=document.createElement('article');card.className='card';const top=document.createElement('div');top.className='card-top';const icon=document.createElement('div');icon.className='icon';icon.textContent=a.icon;const badge=document.createElement('span');badge.className='badge '+(a.broken?'broken':a.mode);badge.textContent=a.broken?'broken':a.mode;top.append(icon,badge);const title=document.createElement('h2');title.textContent=a.title;const meta=document.createElement('div');meta.className='meta';meta.textContent=fmtTime(a.modified)+' · '+fmtSize(a.size);const actions=document.createElement('div');actions.className='actions';const url=new URL(a.open_path,location.href).href;if(!a.broken){const open=document.createElement('a');open.className='action primary';open.href=url;open.textContent='Open';actions.append(open);actions.append(button('Copy','',()=>copyUrl(url)))}actions.append(button('Delete','delete',()=>removeArtifact(a)));card.append(top,title,meta,actions);grid.append(card)}}
async function load(){try{const r=await fetch('/__api/artifacts',{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);artifacts=await r.json();render()}catch(e){grid.innerHTML='<div class="empty"><strong>Could not load artifacts</strong>'+e.message+'</div>'}}
async function removeArtifact(a){if(!confirm('Delete “'+a.title+'”?\n\nThis removes the publication'+(a.mode==='live'?' link, not the original files.':'.')))return;const r=await fetch('/__api/artifacts/delete',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({name:a.name,csrf})});if(!r.ok){toast('Delete failed');return}artifacts=artifacts.filter(x=>x.name!==a.name);toast('Artifact deleted');render()}
$('#search').addEventListener('input',render);$('#refresh').addEventListener('click',load);$('#filters').addEventListener('click',e=>{if(!e.target.dataset.filter)return;filter=e.target.dataset.filter;document.querySelectorAll('.filter').forEach(b=>b.classList.toggle('active',b===e.target));render()});load();
</script>
</body></html>'''


def display_title(name: str) -> str:
    parts = name.split("-", 2)
    value = parts[2] if len(parts) == 3 and len(parts[0]) == 8 and len(parts[1]) == 6 else name
    return value.replace("-", " ").strip().title() or "Artifact"


def directory_size(directory: Path) -> int:
    total = 0
    for root, directories, files in os.walk(directory, followlinks=False):
        directories[:] = [name for name in directories if not (Path(root) / name).is_symlink()]
        for name in files:
            item = Path(root) / name
            if not item.is_symlink():
                try:
                    total += item.stat().st_size
                except OSError:
                    pass
    return total


def artifact_icon(path: Path, is_directory: bool) -> str:
    if is_directory:
        return "WEB"
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "PDF"
    if suffix in {".html", ".htm"}:
        return "HTML"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        return "IMG"
    if suffix in {".zip", ".gz", ".tar", ".7z"}:
        return "ZIP"
    return "FILE"


def describe_artifacts(root: Path) -> list[dict[str, object]]:
    if not root.exists():
        return []
    artifacts = []
    for item in sorted(root.iterdir(), key=lambda value: value.lstat().st_mtime, reverse=True):
        if not item.is_dir() and not item.is_symlink():
            continue
        live = item.is_symlink()
        broken = live and not item.exists()
        is_directory = item.is_dir() if not broken else False
        open_target = item
        if not live and is_directory and not (item / "index.html").is_file():
            files = [child for child in item.iterdir() if child.is_file() and not child.is_symlink()]
            directories = [child for child in item.iterdir() if child.is_dir() and not child.is_symlink()]
            if len(files) == 1 and not directories:
                open_target = files[0]
                is_directory = False
        relative = open_target.relative_to(root)
        open_path = "/".join(quote(part) for part in relative.parts) + ("/" if is_directory else "")
        size = None
        if not broken:
            try:
                size = directory_size(item) if item.is_dir() and not live else (item.stat().st_size if item.is_file() else None)
            except OSError:
                size = None
        artifacts.append({
            "name": item.name,
            "title": display_title(item.name),
            "mode": "live" if live else "snapshot",
            "broken": broken,
            "modified": dt.datetime.fromtimestamp(item.lstat().st_mtime, dt.timezone.utc).isoformat(),
            "size": size,
            "open_path": open_path,
            "icon": artifact_icon(open_target, is_directory),
        })
    return artifacts


class ArtifactHandler(SimpleHTTPRequestHandler):
    server_version = "AgentArtifactServer/2.0"

    @property
    def artifact_root(self) -> Path:
        # Keep the lexical server root for the initial containment check. On
        # macOS, /var is a symlink to /private/var while translate_path keeps
        # the /var spelling; resolving only one side rejects every valid file.
        # Individual publication targets are still resolved below to prevent
        # nested symlink escapes.
        return Path(self.directory).absolute()

    def _path_is_allowed(self) -> bool:
        root = self.artifact_root
        requested = Path(self.translate_path(self.path))
        try:
            relative = requested.relative_to(root)
        except ValueError:
            return False
        if not relative.parts:
            return True
        publication = root / relative.parts[0]
        if not publication.exists():
            return True
        allowed_root = publication.resolve()
        resolved = requested.resolve()
        return resolved == allowed_root or allowed_root in resolved.parents

    def _dashboard(self):
        body = DASHBOARD_HTML.replace("__CSRF_TOKEN__", json.dumps(self.server.csrf_token)).encode()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        return BytesIO(body)

    def send_head(self):
        if urlsplit(self.path).path in {"/", "/index.html"}:
            return self._dashboard()
        if not self._path_is_allowed():
            self.send_error(HTTPStatus.FORBIDDEN, "Artifact path escapes its published root")
            return None
        return super().send_head()

    def do_GET(self) -> None:
        if urlsplit(self.path).path == API_PREFIX:
            self._send_json(HTTPStatus.OK, describe_artifacts(self.artifact_root))
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlsplit(self.path).path != f"{API_PREFIX}/delete":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > MAX_REQUEST_BYTES:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid request size"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid JSON"})
            return
        if not secrets.compare_digest(str(payload.get("csrf", "")), self.server.csrf_token):
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "invalid CSRF token"})
            return
        name = payload.get("name")
        if not isinstance(name, str) or not name or name != Path(name).name:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid artifact name"})
            return
        artifact = self.artifact_root / name
        if not artifact.is_symlink() and not artifact.exists():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "artifact not found"})
            return
        try:
            if artifact.is_symlink():
                artifact.unlink()
            elif artifact.is_dir():
                shutil.rmtree(artifact)
            else:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "not a publication"})
                return
        except OSError as error:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})
            return
        self._send_json(HTTPStatus.OK, {"deleted": name})

    def _send_json(self, status: HTTPStatus, value: object) -> None:
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()


def make_server(bind: str, port: int, root: Path) -> ThreadingHTTPServer:
    root.mkdir(parents=True, exist_ok=True)
    handler = partial(ArtifactHandler, directory=str(root))
    server = ThreadingHTTPServer((bind, port), handler)
    server.daemon_threads = True
    server.csrf_token = secrets.token_urlsafe(32)
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", default=os.environ.get("AGENT_ARTIFACT_BIND", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("AGENT_ARTIFACT_PORT", "8787")))
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("AGENT_ARTIFACT_ROOT", DEFAULT_ROOT)))
    args = parser.parse_args()
    with make_server(args.bind, args.port, args.root.expanduser()) as server:
        host, port = server.server_address[:2]
        print(f"Serving {args.root.expanduser()} on http://{host}:{port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
