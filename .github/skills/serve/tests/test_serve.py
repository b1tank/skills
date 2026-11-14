from __future__ import annotations
import hashlib
import io
import json
import re
import shutil
import subprocess
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import app_registry
import artifact_server
import serve


class ServeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'public'
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def server(self, host='0.0.0.0'):
        server = artifact_server.make_server(host, 0, self.root)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 1)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server

    def test_dashboard_javascript_syntax(self):
        if not shutil.which('node'):
            self.skipTest('Node is not available for JavaScript syntax checking')
        script = re.search(r'<script>(.*?)</script>', artifact_server.DASHBOARD_HTML, re.S)[1]
        result = subprocess.run(['node', '--check'], input=script, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_default_and_reuse_shared_lan_server(self):
        self.assertEqual(serve.DEFAULT_PORT, 12345)
        server = self.server()
        port = server.server_address[1]
        with patch('serve.subprocess.Popen') as launch:
            state = serve.ensure_server(self.root, port)
        launch.assert_not_called()
        self.assertEqual(state['bind'], '0.0.0.0')
        self.assertEqual(state['root_id'], hashlib.sha256(str(self.root.resolve()).encode()).hexdigest())
        self.assertNotIn(str(self.root), json.dumps(state))

    def test_refuses_loopback_only_or_different_portal(self):
        server = self.server('127.0.0.1')
        with self.assertRaisesRegex(ValueError, 'expected LAN'):
            serve.ensure_server(self.root, server.server_address[1])
        server2 = self.server()
        with self.assertRaisesRegex(ValueError, 'expected LAN'):
            serve.ensure_server(self.root / 'different', server2.server_address[1])

    def test_refuses_occupied_port_without_killing(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            with patch('serve.status', return_value=None), patch('serve.subprocess.Popen') as launch:
                with self.assertRaisesRegex(ValueError, 'occupied'):
                    serve.ensure_server(self.root, listener.getsockname()[1])
                launch.assert_not_called()

    def test_refuses_whole_repo_before_starting_server(self):
        repo = Path(self.temp.name) / 'repo'
        (repo / '.git').mkdir(parents=True)
        with patch.object(sys, 'argv', ['serve.py', str(repo)]), patch('serve.ensure_server') as ensure, patch('sys.stderr', new=io.StringIO()):
            self.assertEqual(serve.main(), 1)
        ensure.assert_not_called()

    def test_local_app_validation_and_no_token_storage(self):
        for url in ['https://example.com:8000/', 'http://user:secret@localhost:8000/', 'http://localhost:8000/?token=secret', 'file:///tmp/app']:
            with self.assertRaises(ValueError):app_registry.validate_url(url)
        self.assertEqual(app_registry.validate_url('http://127.0.0.1:8765/#appearances').fragment, 'appearances')

    def test_app_card_and_unregistration_do_not_stop_backend(self):
        backend = self.server()
        port = backend.server_address[1]
        data = app_registry.register(self.root, 'Local demo', f'http://127.0.0.1:{port}/#demo')
        cards = artifact_server.describe_artifacts(self.root)
        self.assertEqual(cards[0]['mode'], 'app')
        self.assertTrue(cards[0]['running'])
        self.assertFalse((self.root / data['name']).exists())
        self.assertTrue(app_registry.remove(self.root, data['name']))
        self.assertTrue(app_registry.reachable(f'http://127.0.0.1:{port}/'))
        self.assertEqual(artifact_server.describe_artifacts(self.root), [])

    def test_offline_app_and_safe_delete_api(self):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0)); unused = probe.getsockname()[1]
        data = app_registry.register(self.root, 'Stopped', f'http://127.0.0.1:{unused}/')
        self.assertFalse(app_registry.cards(self.root)[0]['running'])
        server = self.server()
        request = Request(f'http://127.0.0.1:{server.server_address[1]}/__api/artifacts/delete',
                          data=json.dumps({'name': data['name'], 'csrf': server.csrf_token}).encode(),
                          headers={'Content-Type': 'application/json'}, method='POST')
        with urlopen(request) as response:self.assertEqual(response.status, 200)
        self.assertEqual(app_registry.cards(self.root), [])
        self.assertIn("target.hostname=location.hostname", artifact_server.DASHBOARD_HTML)


if __name__ == '__main__':
    unittest.main()
