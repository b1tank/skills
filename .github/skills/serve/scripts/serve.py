#!/usr/bin/env python3
"""One command: ensure the shared LAN portal, then publish artifacts or register an app."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from publish_artifact import DEFAULT_PORT, DEFAULT_ROOT, local_ipv4_addresses, publish
import app_registry


def status(port: int):
    try:
        with urlopen(f'http://127.0.0.1:{port}/__api/status', timeout=1) as response:
            result = json.load(response)
            return result if isinstance(result, dict) else None
    except (OSError, ValueError, HTTPError, URLError):
        return None


def ensure_server(root: Path, port: int) -> dict:
    root = root.expanduser().absolute()
    root_id = hashlib.sha256(str(root.resolve()).encode()).hexdigest()
    existing = status(port)
    if existing:
        if existing.get('service') != 'agent-artifacts' or existing.get('root_id') != root_id or existing.get('bind') != '0.0.0.0':
            raise ValueError(f'Port {port} is not the expected LAN artifact portal; refusing to replace it')
        return existing
    # Never kill a listener or silently pick another port.
    with socket.socket() as probe:
        try:
            probe.bind(('0.0.0.0', port))
        except OSError as exc:
            raise ValueError(f'Port {port} is occupied; no process was stopped. Choose an explicit --port.') from exc
    root.mkdir(parents=True, exist_ok=True)
    with (root.parent / f'artifact-server-{port}.log').open('a') as log:
        process = subprocess.Popen([sys.executable, str(Path(__file__).with_name('artifact_server.py')),
                                    '--bind', '0.0.0.0', '--port', str(port), '--root', str(root)],
                                   stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    for _ in range(60):
        result = status(port)
        if result:
            if result.get('service') != 'agent-artifacts' or result.get('root_id') != root_id or result.get('bind') != '0.0.0.0':
                raise ValueError('Unexpected server won the port race; refusing to publish')
            return result
        if process.poll() is not None:
            raise ValueError(f'Portal startup failed; inspect artifact-server-{port}.log')
        time.sleep(.1)
    raise ValueError('Portal startup timed out; no publication was created')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts', nargs='*', type=Path)
    parser.add_argument('--root', type=Path, default=Path(os.environ.get('AGENT_ARTIFACT_ROOT', DEFAULT_ROOT)))
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--live', action='store_true', help='Explicitly expose ongoing source edits')
    parser.add_argument('--name')
    parser.add_argument('--app', help='Register an already-running local app; agent handles its approved startup')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        if not 1 <= args.port <= 65535:
            raise ValueError('Port must be 1..65535')
        if args.app and (args.artifacts or args.live):
            raise ValueError('--app cannot be combined with artifact paths or --live')
        if args.name and len(args.artifacts) > 1:
            raise ValueError('--name requires one artifact, or --app')
        for source in args.artifacts:
            path = source.expanduser().resolve()
            if path == Path.home().resolve() or path.parent == path or (path / '.git').exists():
                raise ValueError('Refusing to publish a home/repository root; select the intended output bundle')
            if not path.exists():
                raise ValueError(f'Artifact not found: {path}')
        if args.app:
            parsed = app_registry.validate_url(args.app)
            if not args.name:
                raise ValueError('--app requires a human-readable --name')
            if not app_registry.reachable(args.app):
                raise ValueError('App is not running; start its documented backend before registering it')
            addresses = local_ipv4_addresses()
            if addresses:
                reachable = False
                for address in addresses:
                    try:
                        with socket.create_connection((address, parsed.port), timeout=.5): reachable = True
                    except OSError: pass
                if not reachable:
                    raise ValueError('App is loopback-only; enable approved LAN binding and Host/Origin rules first')
        ensure_server(args.root, args.port)
        os.environ['AGENT_ARTIFACT_PORT'] = str(args.port)
        result = {'portal': f'http://localhost:{args.port}/',
                  'lan_portals': [f'http://{ip}:{args.port}/' for ip in local_ipv4_addresses()],
                  'publications': [publish(p, args.root, args.name, args.live) for p in args.artifacts]}
        if args.app:
            result['app'] = app_registry.register(args.root, args.name, args.app)
        if args.list:
            with urlopen(f'http://127.0.0.1:{args.port}/__api/artifacts', timeout=10) as response:
                result['entries'] = json.load(response)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print('Portal:', result['portal'])
            for url in result['lan_portals']: print('LAN portal:', url)
            for item in result['publications']:
                print('Artifact:', item['url'])
                for url in item['ip_urls']: print('LAN artifact:', url)
            if args.app: print('Registered app:', args.name, '(open its portal card; backend is not copied or proxied)')
            if args.list: print(json.dumps(result['entries'], indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print('serve:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
