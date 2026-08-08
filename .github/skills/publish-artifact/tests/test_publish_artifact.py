#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SKILL_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, SKILL_ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load_module("publish_artifact", "scripts/publish_artifact.py")
server_module = load_module("artifact_server", "scripts/artifact_server.py")


class PublishArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.public = self.base / "public"
        self.when = publisher.dt.datetime(2026, 8, 1, 12, 30, 45, tzinfo=publisher.dt.timezone.utc)
        self.original_unique_destination = publisher.unique_destination
        publisher.unique_destination = lambda root, label: self.original_unique_destination(root, label, self.when)

    def tearDown(self) -> None:
        publisher.unique_destination = self.original_unique_destination
        self.temporary.cleanup()

    def test_publishes_file_without_overwriting(self) -> None:
        source = self.base / "Quarterly Report.pdf"
        source.write_bytes(b"%PDF-test")

        first = publisher.publish(source, self.public, "Review Copy")
        second = publisher.publish(source, self.public, "Review Copy")

        self.assertTrue((Path(first["published"]) / source.name).is_file())
        self.assertEqual(first["url"], "http://localhost:8787/20260801-123045-review-copy/Quarterly%20Report.pdf")
        self.assertTrue(Path(second["published"]).name.endswith("-2"))

    def test_publishes_directory_with_relative_assets(self) -> None:
        source = self.base / "site"
        (source / "assets").mkdir(parents=True)
        (source / "index.html").write_text('<img src="assets/chart.png">', encoding="utf-8")
        (source / "assets" / "chart.png").write_bytes(b"png")

        result = publisher.publish(source, self.public)

        published = Path(result["published"])
        self.assertEqual((published / "index.html").read_text(encoding="utf-8"), '<img src="assets/chart.png">')
        self.assertEqual((published / "assets" / "chart.png").read_bytes(), b"png")
        self.assertTrue(result["url"].endswith("/20260801-123045-site/"))

    def test_rejects_symlinks(self) -> None:
        source = self.base / "site"
        source.mkdir()
        target = self.base / "secret"
        target.write_text("do not publish", encoding="utf-8")
        (source / "linked-secret").symlink_to(target)

        with self.assertRaisesRegex(ValueError, "symbolic link"):
            publisher.publish(source, self.public)

    def test_live_directory_reflects_edits(self) -> None:
        source = self.base / "live-site"
        source.mkdir()
        page = source / "index.html"
        page.write_text("first", encoding="utf-8")

        result = publisher.publish(source, self.public, live=True)
        published = Path(result["published"])
        self.assertTrue(published.is_symlink())
        self.assertEqual(result["mode"], "live")
        self.assertEqual((published / "index.html").read_text(encoding="utf-8"), "first")

        page.write_text("second", encoding="utf-8")
        self.assertEqual((published / "index.html").read_text(encoding="utf-8"), "second")

    def test_live_file_keeps_extension(self) -> None:
        source = self.base / "report.pdf"
        source.write_bytes(b"%PDF-live")

        result = publisher.publish(source, self.public, live=True)

        self.assertTrue(Path(result["published"]).is_symlink())
        self.assertTrue(result["url"].endswith(".pdf"))
        self.assertEqual(result["type"], "live-file")

    def test_server_serves_only_public_root_with_safe_headers(self) -> None:
        self.public.mkdir()
        (self.public / "report.html").write_text("<h1>ready</h1>", encoding="utf-8")
        outside = self.base / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        server = server_module.make_server("127.0.0.1", 0, self.public)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.05)
        try:
            port = server.server_address[1]
            with urlopen(f"http://127.0.0.1:{port}/report.html") as response:
                self.assertEqual(response.read(), b"<h1>ready</h1>")
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
            with self.assertRaises(Exception):
                urlopen(f"http://127.0.0.1:{port}/../outside.txt")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_homepage_lists_artifacts_and_delete_requires_csrf(self) -> None:
        snapshot = self.public / "20260801-123045-report"
        snapshot.mkdir(parents=True)
        (snapshot / "report.pdf").write_bytes(b"%PDF-test")
        server = server_module.make_server("127.0.0.1", 0, self.public)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            base = f"http://127.0.0.1:{port}"
            with urlopen(f"{base}/") as response:
                homepage = response.read().decode()
                self.assertIn("Agent Artifacts", homepage)
                self.assertNotIn("Directory listing for", homepage)
            with urlopen(f"{base}/__api/artifacts") as response:
                artifacts = json.loads(response.read())
                self.assertEqual(artifacts[0]["title"], "Report")
                self.assertEqual(artifacts[0]["open_path"], "20260801-123045-report/report.pdf")

            bad = Request(
                f"{base}/__api/artifacts/delete",
                data=b'{"name":"20260801-123045-report","csrf":"wrong"}',
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as denied:
                urlopen(bad)
            self.assertEqual(denied.exception.code, 403)
            self.assertTrue(snapshot.exists())

            payload = json.dumps({"name": snapshot.name, "csrf": server.csrf_token}).encode()
            delete = Request(
                f"{base}/__api/artifacts/delete",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(delete) as response:
                self.assertEqual(response.status, 200)
            self.assertFalse(snapshot.exists())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_delete_live_publication_preserves_original(self) -> None:
        source = self.base / "original"
        source.mkdir()
        (source / "index.html").write_text("keep", encoding="utf-8")
        self.public.mkdir()
        publication = self.public / "live-publication"
        publication.symlink_to(source, target_is_directory=True)
        server = server_module.make_server("127.0.0.1", 0, self.public)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            payload = json.dumps({"name": publication.name, "csrf": server.csrf_token}).encode()
            request = Request(
                f"http://127.0.0.1:{port}/__api/artifacts/delete",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request) as response:
                self.assertEqual(response.status, 200)
            self.assertFalse(publication.is_symlink())
            self.assertEqual((source / "index.html").read_text(encoding="utf-8"), "keep")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def test_server_allows_live_root_but_blocks_escaping_nested_symlink(self) -> None:
        source = self.base / "live"
        source.mkdir()
        (source / "index.html").write_text("live", encoding="utf-8")
        secret = self.base / "secret.txt"
        secret.write_text("secret", encoding="utf-8")
        publication = self.public / "live-publication"
        self.public.mkdir()
        publication.symlink_to(source, target_is_directory=True)
        server = server_module.make_server("127.0.0.1", 0, self.public)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            with urlopen(f"http://127.0.0.1:{port}/live-publication/") as response:
                self.assertEqual(response.read(), b"live")

            (source / "escape.txt").symlink_to(secret)
            with self.assertRaises(Exception):
                urlopen(f"http://127.0.0.1:{port}/live-publication/escape.txt")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)


if __name__ == "__main__":
    unittest.main()
