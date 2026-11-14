#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import sys
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


sys.path.insert(0, str(SKILL_ROOT / 'scripts'))
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

    def test_latest_publication_first_despite_copied_mtime(self) -> None:
        older = self.public / '20260801-123045-older'
        newer = self.public / '20260802-123045-newer'
        older.mkdir(parents=True)
        newer.mkdir()
        os.utime(older, (2000, 2000))
        os.utime(newer, (1000, 1000))

        for records in [publisher.publications(self.public), server_module.describe_artifacts(self.public)]:
            self.assertEqual([r['name'] for r in records], [newer.name, older.name])
            self.assertEqual(records[0]['published_at'], '2026-08-02T12:30:45+00:00')
            self.assertEqual(records[0]['modified'], '1970-01-01T00:16:40+00:00')

        # A later edit to an older live target must not make it a new publication.
        target = self.base / 'target'
        target.mkdir()
        live = self.public / '20260701-000000-live'
        live.symlink_to(target, target_is_directory=True)
        os.utime(target, (4000000000, 4000000000))
        self.assertEqual(server_module.describe_artifacts(self.public)[0]['name'], newer.name)

    def test_identical_copied_times_and_natural_collision_order(self) -> None:
        self.public.mkdir()
        names = ['20260801-123045-report', '20260801-123045-report-2', '20260801-123045-report-10']
        for name in names:
            path = self.public / name
            path.mkdir()
            os.utime(path, (1000, 1000))
        expected = list(reversed(names))
        self.assertEqual([r['name'] for r in server_module.describe_artifacts(self.public)], expected)
        self.assertEqual([r['name'] for r in publisher.publications(self.public)], expected)

    def test_legacy_and_invalid_dates_fall_back_without_false_publication_date(self) -> None:
        self.public.mkdir()
        for name, timestamp in [('legacy', 2000), ('20269999-999999-invalid', 1000)]:
            path = self.public / name
            path.mkdir()
            os.utime(path, (timestamp, timestamp))
        records = server_module.describe_artifacts(self.public)
        self.assertEqual([r['name'] for r in records], ['legacy', '20269999-999999-invalid'])
        self.assertTrue(all(r['published_at'] is None for r in records))
        self.assertIn("a.published_at||a.modified", server_module.DASHBOARD_HTML)
        self.assertIn('Newest publications first, from the top-left', server_module.DASHBOARD_HTML)

    def test_prune_uses_publication_age_not_copied_mtime(self) -> None:
        self.public.mkdir()
        stamp = publisher.dt.datetime.now(publisher.dt.timezone.utc).strftime('%Y%m%d-%H%M%S')
        fresh = self.public / (stamp + '-fresh')
        old = self.public / '20000101-000000-old'
        fresh.mkdir(); old.mkdir()
        os.utime(fresh, (1000, 1000))
        self.assertEqual(publisher.prune(self.public, 1), [old.name])
        self.assertTrue(fresh.exists())

    def test_broken_live_link_keeps_publication_date(self) -> None:
        self.public.mkdir()
        path = self.public / '20260802-123045-broken.pdf'
        path.symlink_to(self.base / 'missing.pdf')
        records = server_module.describe_artifacts(self.public)
        self.assertTrue(records[0]['broken'])
        self.assertEqual(records[0]['published_at'], '2026-08-02T12:30:45+00:00')

    def test_publishes_file_without_overwriting(self) -> None:
        source = self.base / "Quarterly Report.pdf"
        source.write_bytes(b"%PDF-test")

        first = publisher.publish(source, self.public, "Review Copy")
        second = publisher.publish(source, self.public, "Review Copy")

        self.assertTrue((Path(first["published"]) / source.name).is_file())
        self.assertEqual(first["url"], "http://localhost:12345/20260801-123045-review-copy/Quarterly%20Report.pdf")
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
                self.assertEqual(artifacts[0]['published_at'], '2026-08-01T12:30:45+00:00')

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
