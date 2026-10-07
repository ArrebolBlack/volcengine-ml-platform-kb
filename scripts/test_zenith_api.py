import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

import zenith_api as api


class ZenithApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.token = self.root / "zenith.env"
        self.token.write_text("ZENITH_API_TOKEN=file-example\n", encoding="utf-8")
        self.key = self.root / "intent.key"
        self.key.write_text("test-intent-key-123\n", encoding="utf-8")
        self.body = self.root / "body.json"
        self.body.write_text('{"name":"中文任务"}', encoding="utf-8-sig")

    def run_cli(self, arguments):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = api.main(["--base-url", "http://zenith.example", "--token-file", str(self.token)] + arguments)
        return code, out.getvalue(), err.getvalue()

    def test_environment_precedes_file_and_file_is_strict(self):
        with patch.dict(os.environ, {"ZENITH_API_TOKEN": "env-example"}):
            self.assertEqual(api.read_token("missing-file"), "env-example")
        with patch.dict(os.environ, {"ZENITH_API_TOKEN": ""}):
            self.assertEqual(api.read_token(self.token), "file-example")
            for value in ("bad=secret", "ZENITH_API_TOKEN=a\nextra=x", "ZENITH_API_TOKEN=a b", "ZENITH_API_TOKEN="):
                self.token.write_text(value, encoding="utf-8")
                with self.assertRaises(ValueError):
                    api.read_token(self.token)

    def test_url_and_endpoint_boundaries(self):
        for path, method in (
            ("https://elsewhere.example/pt/api/ai/instances", "GET"),
            ("//elsewhere.example/pt/api/ai/instances", "GET"),
            ("/pt/api/ai/files/bucket-sts", "POST"),
            ("/pt/api/ai/files/download-presign", "POST"),
            ("/pt/api/ai/datasets/abc/file", "GET"),
            ("/pt/api/ai/datasets/%2e%2e", "GET"),
            ("/pt/api/me/ssh-keys", "POST"),
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                api.checked_url("http://zenith.example", path, method)
        self.assertEqual(api.checked_url("http://zenith.example", "http://zenith.example/pt/api/ai/jobs?page=2", "GET"), "http://zenith.example/pt/api/ai/jobs?page=2")

    @patch.dict(os.environ, {"ZENITH_API_TOKEN": ""})
    def test_post_keeps_key_and_sends_utf8(self):
        with patch.object(api, "request", return_value=(202, b'{"operation_id":"abc","state":"CLAIMED"}', None)) as send:
            arguments = ["post", "/pt/api/compute-offerings/offering/jobs", "--body-file", str(self.body), "--key-file", str(self.key)]
            for _ in range(2):
                code, out, err = self.run_cli(arguments)
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(out)["state"], "CLAIMED")
                self.assertIn("HTTP 202", err)
            self.assertEqual(send.call_count, 2)
            for call in send.call_args_list:
                self.assertEqual(call.args[4], "test-intent-key-123")
                self.assertEqual(json.loads(call.args[5].decode("utf-8"))["name"], "中文任务")
                self.assertFalse(call.args[5].startswith(b"\xef\xbb\xbf"))

    @patch.dict(os.environ, {"ZENITH_API_TOKEN": ""})
    def test_lost_response_never_retries(self):
        with patch.object(api, "request", side_effect=URLError("timed out")) as send:
            code, out, err = self.run_cli(["post", "/pt/api/compute-offerings/offering/jobs", "--body-file", str(self.body), "--key-file", str(self.key)])
            self.assertEqual(code, 1)
            send.assert_called_once()
            self.assertEqual(out, "")
            self.assertIn("operations/by-key", err)
            self.assertNotIn("file-example", err)

    def test_unknown_wait_preserves_envelope_and_exits(self):
        payload = b'{"operation":{"operation_id":"aaaaaaaaaaaaaaaaaaaaaaaaa","state":"UNKNOWN"}}'
        with patch.object(api, "request", return_value=(200, payload, None)) as send, patch.object(api.time, "sleep") as sleep:
            code, out, err = self.run_cli(["wait", "a" * 25])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out)["operation"]["state"], "UNKNOWN")
            self.assertIn("retain the original key", err)
            send.assert_called_once()
            sleep.assert_not_called()

    def test_wait_polls_every_five_seconds_and_does_not_claim_running(self):
        replies = [(200, b'{"operation":{"state":"RUNNING"}}', None), (200, b'{"operation":{"state":"SUCCEEDED"}}', None)]
        with patch.object(api, "request", side_effect=replies), patch.object(api.time, "sleep") as sleep:
            code, out, err = self.run_cli(["wait", "a" * 25])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["operation"]["state"], "SUCCEEDED")
            sleep.assert_called_once_with(5)
            self.assertIn("does not mean", err)
        with patch.object(api, "request", return_value=replies[0]), patch.object(api.time, "sleep") as sleep:
            code, out, err = self.run_cli(["wait", "a" * 25, "--timeout", "1"])
            self.assertEqual(code, 1)
            self.assertIn("Wait timeout", err)
            sleep.assert_not_called()

    def test_http_error_keeps_receipt(self):
        payload = b'{"operation_id":"aaaaaaaaaaaaaaaaaaaaaaaaa","state":"FAILED"}'
        opener = Mock()
        opener.open.side_effect = HTTPError("http://zenith.example", 502, "Bad Gateway", {}, io.BytesIO(payload))
        self.assertEqual(api.request(opener, "POST", "http://zenith.example", "example", body=b"{}"), (502, payload, None))
        with patch.object(api, "build_opener", return_value=opener):
            opener.open.side_effect = HTTPError("http://zenith.example", 502, "Bad Gateway", {}, io.BytesIO(payload))
            code, out, err = self.run_cli(["post", "/pt/api/compute-offerings/offering/jobs", "--body-file", str(self.body), "--key-file", str(self.key)])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out)["state"], "FAILED")
            self.assertIn("HTTP 502", err)

    def test_schema_is_anonymous_and_redirects_are_refused(self):
        with patch.object(api, "read_token") as token, patch.object(api, "request", return_value=(200, b"{}", None)) as send:
            self.assertEqual(self.run_cli(["schema"])[0], 0)
            token.assert_not_called()
            self.assertIsNone(send.call_args.args[3])
        self.assertIsNone(api.NoRedirect().redirect_request(None, None, 302, "", {}, "http://elsewhere.example"))

    def test_key_required_and_by_key_recovery(self):
        with patch.object(api, "request", return_value=(200, b'{"operation":{"state":"RUNNING"}}', None)) as send:
            self.assertEqual(self.run_cli(["post", "/pt/api/compute-offerings/offering/jobs", "--body-file", str(self.body)])[0], 1)
            self.assertEqual(self.run_cli(["get", "/pt/api/operations/by-key"])[0], 1)
            send.assert_not_called()
            self.assertEqual(self.run_cli(["get", "/pt/api/operations/by-key", "--key-file", str(self.key)])[0], 0)
            self.assertEqual(send.call_args.args[4], "test-intent-key-123")
            self.assertEqual(self.run_cli(["post", "/pt/api/compute-offerings/offering/admission", "--body-file", str(self.body)])[0], 0)

    def test_retry_after_controls_polling_with_finite_timeout(self):
        running = (200, b'{"operation":{"state":"RUNNING"}}', "12")
        finished = (200, b'{"operation":{"state":"SUCCEEDED","finalization_state":"SUCCEEDED"}}', None)
        with patch.object(api, "request", side_effect=[running, finished]), patch.object(api.time, "sleep") as sleep:
            code, out, err = self.run_cli(["wait", "a" * 25])
            self.assertEqual(code, 0)
            sleep.assert_called_once_with(12)
            self.assertIn("Retry-After: 12", err)
        with patch.object(api, "request", return_value=running) as send, patch.object(api.time, "sleep") as sleep:
            code, out, err = self.run_cli(["wait", "a" * 25, "--timeout", "10"])
            self.assertEqual(code, 1)
            send.assert_called_once()
            sleep.assert_not_called()
            self.assertIn("Wait timeout", err)
        self.assertEqual(api.poll_delay("2"), 5)
        with patch.object(api.time, "time", return_value=0):
            self.assertEqual(api.poll_delay("Thu, 01 Jan 1970 00:00:15 GMT"), 15)

    def test_rate_limit_preserves_retry_after_and_does_not_retry(self):
        payload = b'{"error":"Rate limited"}'
        opener = Mock()
        opener.open.side_effect = HTTPError("http://zenith.example", 429, "Too Many Requests", {"Retry-After": "60"}, io.BytesIO(payload))
        with patch.object(api, "build_opener", return_value=opener), patch.object(api.time, "sleep") as sleep:
            code, out, err = self.run_cli(["wait", "a" * 25])
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(out)["error"], "Rate limited")
            self.assertIn("Retry-After: 60", err)
            opener.open.assert_called_once()
            sleep.assert_not_called()

    def test_unresolved_finalization_is_not_success(self):
        for state in ("PENDING", "RETRYING", "NEEDS_RECONCILIATION"):
            payload = json.dumps({"operation": {"state": "SUCCEEDED", "finalization_state": state}}).encode()
            with self.subTest(state=state), patch.object(api, "request", return_value=(200, payload, None)):
                code, out, err = self.run_cli(["wait", "a" * 25])
                self.assertEqual(code, 1)
                self.assertEqual(json.loads(out)["operation"]["finalization_state"], state)
                self.assertIn("finalization_state: " + state, err)
                self.assertIn("finalization is unresolved", err)


if __name__ == "__main__":
    unittest.main()
