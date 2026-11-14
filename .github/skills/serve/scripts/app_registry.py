"""Allowlisted local-app links, not a proxy or browser-triggered process launcher."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import socket
from urllib.parse import urlsplit
from publish_artifact import slugify


def registry(root: Path) -> Path:
    return root.absolute().parent / (root.name + '-apps')


def validate_url(url: str):
    parsed = urlsplit(url)
    if parsed.scheme not in {'http', 'https'} or parsed.hostname not in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('App URL must be an explicitly approved local HTTP(S) backend')
    if parsed.username or parsed.password or parsed.query:
        raise ValueError('Do not store credentials or query tokens in app registrations')
    if not parsed.port:
        raise ValueError('Specify the local app port')
    return parsed


def reachable(url: str, timeout: float = .15) -> bool:
    parsed = validate_url(url)
    try:
        with socket.create_connection((parsed.hostname, parsed.port), timeout=timeout):
            return True
    except OSError:
        return False


def register(root: Path, name: str, url: str) -> dict:
    validate_url(url)
    identifier = 'app-' + slugify(name)
    folder = registry(root)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    data = dict(name=identifier, title=name, app_url=url, published_at=stamp)
    temporary = folder / (identifier + '.tmp')
    temporary.write_text(json.dumps(data, indent=2))
    temporary.replace(folder / (identifier + '.json'))
    return data


def cards(root: Path) -> list[dict]:
    folder = registry(root)
    result = []
    if not folder.exists():
        return result
    for file in folder.glob('app-*.json'):
        if file.is_symlink():
            continue
        try:
            data = json.loads(file.read_text())
            validate_url(data['app_url'])
            if data['name'] != file.stem or not isinstance(data['title'], str):
                continue
            dt.datetime.fromisoformat(data['published_at'])
            running = reachable(data['app_url'])
            result.append(dict(**data, mode='app', running=running, broken=not running,
                               modified=data['published_at'], size=None, open_path='', icon='APP'))
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return result


def remove(root: Path, name: str) -> bool:
    if not name.startswith('app-') or name != Path(name).name:
        return False
    file = registry(root) / (name + '.json')
    if file.is_file() and not file.is_symlink():
        file.unlink()
        return True
    return False
