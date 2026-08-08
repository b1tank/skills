#!/usr/bin/env python3
"""Copy one artifact into the dedicated LAN/VPN publication directory."""

from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sys
from typing import Any
from urllib.parse import quote

DEFAULT_ROOT = Path.home() / ".local" / "share" / "agent-artifacts" / "public"
DEFAULT_HOST = os.environ.get("AGENT_ARTIFACT_HOST", "localhost")
DEFAULT_PORT = int(os.environ.get("AGENT_ARTIFACT_PORT", "8787"))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "artifact"


def reject_symlinks(source: Path) -> None:
    if source.is_symlink():
        raise ValueError(f"Refusing to publish a symbolic link: {source}")
    if source.is_dir():
        for root, directories, files in os.walk(source, followlinks=False):
            for name in [*directories, *files]:
                candidate = Path(root) / name
                if candidate.is_symlink():
                    raise ValueError(f"Refusing directory containing a symbolic link: {candidate}")


def unique_destination(root: Path, label: str, now: dt.datetime | None = None) -> Path:
    timestamp = (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y%m%d-%H%M%S")
    base = root / f"{timestamp}-{slugify(label)}"
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = root / f"{base.name}-{suffix}"
        suffix += 1
    return candidate


def local_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            address = info[4][0]
            parsed = ipaddress.ip_address(address)
            if not parsed.is_loopback and not parsed.is_link_local:
                addresses.add(address)
    except socket.gaierror:
        pass

    # UDP connect chooses the normal outbound interface without sending traffic.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 80))
            address = sock.getsockname()[0]
            if not ipaddress.ip_address(address).is_loopback:
                addresses.add(address)
    except OSError:
        pass
    return sorted(addresses, key=lambda value: tuple(int(part) for part in value.split(".")))


def encoded_path(parts: tuple[str, ...]) -> str:
    return "/".join(quote(part) for part in parts)


def live_destination(root: Path, label: str, suffix: str) -> Path:
    candidate = unique_destination(root, label)
    if suffix:
        candidate = candidate.with_name(f"{candidate.name}{suffix.lower()}")
    base = candidate
    number = 2
    while candidate.exists() or candidate.is_symlink():
        candidate = base.with_name(f"{base.stem}-{number}{base.suffix}")
        number += 1
    return candidate


def publish(source: Path, root: Path, name: str | None = None, live: bool = False) -> dict[str, Any]:
    source = source.expanduser().absolute()
    if not source.exists():
        raise FileNotFoundError(f"Artifact does not exist: {source}")
    if not source.is_file() and not source.is_dir():
        raise ValueError(f"Artifact must be a regular file or directory: {source}")
    reject_symlinks(source)

    root.mkdir(parents=True, exist_ok=True)
    label = name or source.stem or source.name
    if live:
        destination = live_destination(root, label, source.suffix if source.is_file() else "")
        destination.symlink_to(source, target_is_directory=source.is_dir())
        relative_parts = (destination.name, "") if source.is_dir() else (destination.name,)
        artifact_type = "live-directory" if source.is_dir() else "live-file"
    else:
        destination = unique_destination(root, label)
        if source.is_dir():
            shutil.copytree(source, destination, symlinks=True)
            relative_parts = (destination.name, "")
            artifact_type = "directory"
        else:
            destination.mkdir()
            copied = destination / source.name
            shutil.copy2(source, copied, follow_symlinks=False)
            relative_parts = (destination.name, copied.name)
            artifact_type = "file"

    path = encoded_path(relative_parts)
    host = os.environ.get("AGENT_ARTIFACT_HOST", DEFAULT_HOST)
    port = int(os.environ.get("AGENT_ARTIFACT_PORT", str(DEFAULT_PORT)))
    result: dict[str, Any] = {
        "source": str(source),
        "published": str(destination),
        "type": artifact_type,
        "mode": "live" if live else "snapshot",
        "url": f"http://{host}:{port}/{path}",
        "local_url": f"http://127.0.0.1:{port}/{path}",
        "ip_urls": [f"http://{address}:{port}/{path}" for address in local_ipv4_addresses()],
    }
    return result


def publications(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    output = []
    for item in sorted(root.iterdir(), key=lambda path: path.lstat().st_mtime, reverse=True):
        if (item.is_dir() and not item.is_symlink()) or item.is_symlink():
            output.append({
                "name": item.name,
                "path": str(item),
                "mode": "live" if item.is_symlink() else "snapshot",
                "modified": dt.datetime.fromtimestamp(item.lstat().st_mtime, dt.timezone.utc).isoformat(),
            })
    return output


def prune(root: Path, days: int) -> list[str]:
    if days < 1:
        raise ValueError("--prune-days must be at least 1")
    cutoff = dt.datetime.now(dt.timezone.utc).timestamp() - days * 86400
    removed: list[str] = []
    for item in root.iterdir() if root.exists() else []:
        if item.lstat().st_mtime >= cutoff:
            continue
        if item.is_symlink():
            item.unlink()
            removed.append(item.name)
        elif item.is_dir():
            shutil.rmtree(item)
            removed.append(item.name)
    return sorted(removed)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("artifact", nargs="?", type=Path)
    result.add_argument("--name", help="Human-readable URL label")
    result.add_argument("--live", action="store_true", help="Serve the original path so edits appear at the same URL")
    result.add_argument("--root", type=Path, default=Path(os.environ.get("AGENT_ARTIFACT_ROOT", DEFAULT_ROOT)))
    result.add_argument("--json", action="store_true", help="Print structured output")
    result.add_argument("--list", action="store_true", help="List existing publications")
    result.add_argument("--prune-days", type=int, help="Delete publications older than this many days")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.list:
            result: Any = publications(args.root)
        elif args.prune_days is not None:
            result = {"removed": prune(args.root, args.prune_days)}
        elif args.artifact:
            result = publish(args.artifact, args.root, args.name, args.live)
        else:
            raise ValueError("Provide an artifact path, --list, or --prune-days")
    except (OSError, ValueError) as error:
        print(f"publish-artifact: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    elif isinstance(result, dict) and "url" in result:
        print(result["url"])
        for url in result["ip_urls"]:
            print(f"IP fallback: {url}")
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
