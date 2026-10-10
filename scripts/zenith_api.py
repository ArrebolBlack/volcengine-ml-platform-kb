#!/usr/bin/env python3
"""Small standard-library HTTP entry point for Zenith Personal API; not an official CLI."""

import argparse
from email.utils import parsedate_to_datetime
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


# Deliberately excludes STS, signed URLs, file contents and credential mutations.
SEGMENT = r"[A-Za-z0-9_:-][A-Za-z0-9_.:-]*"
GET_PATHS = (
    r"/pt/api/ai/capabilities",
    r"/pt/api/me(?:/quota-usage|/card-hours|/mount-disks|/bucket-mounts|/ssh-keys)?",
    rf"/pt/api/me/ssh-keys/{SEGMENT}",
    rf"/pt/api/projects(?:/{SEGMENT})?",
    rf"/pt/api/compute-offerings(?:/{SEGMENT}/images)?",
    rf"/pt/api/ai/instances(?:/{SEGMENT}(?:/{SEGMENT})?)?",
    rf"/pt/api/ai/instances/{SEGMENT}(?:/{SEGMENT})?/mounts",
    rf"/pt/api/instances/{SEGMENT}(?:/{SEGMENT})?/(?:ssh-access|ssh-injections)",
    rf"/pt/api/ai/jobs(?:/{SEGMENT}/{SEGMENT}(?:/(?:logs|replicas|metrics))?)?",
    rf"/pt/api/operations/{SEGMENT}",
    r"/pt/api/ai/files/sources",
    rf"/pt/api/ai/datasets(?:/{SEGMENT})?",
)
POST_PATHS = (
    rf"/pt/api/compute-offerings/{SEGMENT}/(?:instances|jobs|admission)",
    rf"/pt/api/ai/instances/{SEGMENT}(?:/{SEGMENT})?/(?:start|stop|restart)",
    rf"/pt/api/instances/{SEGMENT}(?:/{SEGMENT})?/resize",
    rf"/pt/api/ai/jobs/{SEGMENT}/{SEGMENT}/cancel",
    rf"/pt/api/operations/{SEGMENT}/cancel-job",
)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def checked_url(base_url, target, method, schema=False):
    if not base_url:
        raise ValueError("Set --base-url or ZENITH_BASE_URL to the intended Zenith origin.")
    if any(c.isspace() or ord(c) < 32 or c == "\\" for c in base_url + target):
        raise ValueError("URLs must not contain whitespace, controls or backslashes.")
    base = urlsplit(base_url)
    if (base.scheme not in ("http", "https") or not base.hostname
            or base.username is not None or base.password is not None
            or base.path not in ("", "/") or base.query or base.fragment):
        raise ValueError("--base-url must be an HTTP(S) origin without credentials or a path.")

    def origin(parts):
        return parts.scheme, parts.hostname, parts.port or (443 if parts.scheme == "https" else 80)

    requested = urlsplit(target)
    if requested.scheme or requested.netloc:
        if (origin(requested) != origin(base) or requested.username is not None
                or requested.password is not None):
            raise ValueError("Cross-origin URLs and URL credentials are forbidden.")
    elif not target.startswith("/"):
        raise ValueError("Use an absolute /pt/api/... path or a same-origin URL.")
    if requested.fragment or "%" in requested.path:
        raise ValueError("Fragments and percent-encoded API paths are unsupported.")
    patterns = (r"/pt/api/openapi\.json",) if schema else GET_PATHS if method == "GET" else POST_PATHS
    if not any(re.fullmatch(pattern, requested.path) for pattern in patterns):
        raise ValueError("Endpoint is outside this compute helper's allowlist; inspect the official API documentation.")
    return urlunsplit((base.scheme, base.netloc, requested.path, requested.query, ""))


def read_token(token_file=None):
    token = os.environ.get("ZENITH_API_TOKEN", "")
    if not token.strip():
        if not token_file:
            raise ValueError("Set ZENITH_API_TOKEN or pass --token-file; no credential is read implicitly.")
        lines = Path(token_file).read_text(encoding="utf-8-sig").splitlines()
        if len(lines) != 1 or not re.fullmatch(r"ZENITH_API_TOKEN=\S+", lines[0]):
            raise ValueError("Token file must contain exactly one line: ZENITH_API_TOKEN=<token>.")
        token = lines[0].split("=", 1)[1]
    if not re.fullmatch(r"[!-~]+", token):
        raise ValueError("ZENITH_API_TOKEN must be one nonempty ASCII value without whitespace.")
    return token


def read_key(key_file):
    lines = Path(key_file).read_text(encoding="utf-8-sig").splitlines()
    if len(lines) != 1 or not re.fullmatch(r"[!-~]{8,200}", lines[0]):
        raise ValueError("Key file must contain one existing 8-200 character ASCII key without whitespace.")
    return lines[0]


def read_body(body_file):
    # Accept PowerShell's UTF-8 BOM, but send canonical UTF-8 bytes without it.
    body = json.loads(Path(body_file).read_text(encoding="utf-8-sig"))
    if not isinstance(body, dict):
        raise ValueError("Request body must be a JSON object.")
    return json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")


def request(opener, method, url, token, key=None, body=None, timeout=30):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if key:
        headers["Idempotency-Key"] = key
    if body is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(req, timeout=timeout) as response:
            return response.status, response.read(), response.headers.get("Retry-After")
    except HTTPError as exc:
        # Failed mutations can still include a durable receipt; keep its body.
        with exc:
            return exc.code, exc.read(), exc.headers.get("Retry-After")


def output_response(status, body, retry_after=None):
    print(f"HTTP {status}", file=sys.stderr)
    if retry_after is not None:
        print(f"Retry-After: {retry_after}", file=sys.stderr)
    text = body.decode("utf-8-sig")
    if text:
        print(text)
    if 300 <= status < 400:
        print("Redirect refused; verify --base-url. No request was sent to the redirect target.", file=sys.stderr)
    if status == 429:
        print("Rate limited; no automatic retry. Respect Retry-After before resuming with the same operation ID/key.", file=sys.stderr)
    return 0 if 200 <= status < 300 else 1


def poll_delay(retry_after):
    if retry_after is None:
        return 5
    if re.fullmatch(r"\d+", retry_after):
        return max(5, int(retry_after))
    try:
        return max(5, parsedate_to_datetime(retry_after).timestamp() - time.time())
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Invalid Retry-After header; inspect the server response before polling again.") from None


def wait_operation(opener, url, token, timeout, request_timeout):
    deadline = time.monotonic() + timeout
    while True:
        status, body, retry_after = request(opener, "GET", url, token, timeout=min(request_timeout, max(0.001, deadline - time.monotonic())))
        if not 200 <= status < 300:
            return output_response(status, body, retry_after)
        try:
            operation = json.loads(body)["operation"]
            state = operation["state"]
        except (ValueError, KeyError, TypeError):
            output_response(status, body, retry_after)
            raise ValueError("Expected the documented {operation: {state: ...}} response.") from None
        if state == "SUCCEEDED":
            output_response(status, body, retry_after)
            finalization = operation.get("finalization_state")
            print(f"Platform finalization_state: {finalization or 'not reported'}.", file=sys.stderr)
            if finalization not in (None, "SUCCEEDED"):
                print("Provider call succeeded, but platform finalization is unresolved. Retain the original key; inspect the resource and operation before continuing. Do not create with a new key.", file=sys.stderr)
                return 1
            print("Operation succeeded; this does not mean the instance/job is running. Read its resource URL and actual state.", file=sys.stderr)
            return 0
        if state in ("FAILED", "UNKNOWN"):
            output_response(status, body, retry_after)
            print(f"Operation is {state}; retain the original key and reconcile. Do not create with a new key.", file=sys.stderr)
            return 1
        if state not in ("CLAIMED", "RUNNING"):
            output_response(status, body, retry_after)
            raise ValueError("Unexpected operation state; inspect the response before continuing.")
        try:
            delay = poll_delay(retry_after)
        except ValueError:
            output_response(status, body, retry_after)
            raise
        remaining = deadline - time.monotonic()
        if remaining <= delay:
            output_response(status, body, retry_after)
            print("Wait timeout: insufficient time for the next permitted poll; operation may still be active. Reuse its ID/key to inspect it.", file=sys.stderr)
            return 1
        if retry_after is not None:
            print(f"Retry-After: {retry_after}", file=sys.stderr)
        print(f"Operation {state}; polling again in {delay:g} seconds.", file=sys.stderr)
        time.sleep(delay)


def parser():
    result = argparse.ArgumentParser(
        description="Zenith Personal API HTTP helper (Python standard library), NOT the official CLI and does not require it.",
        epilog="Global options precede the command. Prints the service response to stdout and diagnostics to stderr. Never retries a POST. Only run mutations you have authorized.",
    )
    result.add_argument("--base-url", default=os.environ.get("ZENITH_BASE_URL"), help="Explicit Zenith HTTP(S) origin, or ZENITH_BASE_URL")
    result.add_argument("--token-file", help="Single-line ZENITH_API_TOKEN=... file; nonempty environment variable takes precedence")
    result.add_argument("--direct", action="store_true", help="Explicitly bypass configured HTTP proxies")
    result.add_argument("--request-timeout", type=float, default=30, help="Per-request timeout in seconds (default: 30)")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("schema", help="Read OpenAPI anonymously; token is neither loaded nor sent")
    get = commands.add_parser("get", help="Read an allowed compute/catalog API endpoint")
    get.add_argument("path")
    get.add_argument("--key-file", help="Original key file; required only for /pt/api/operations/by-key")
    post = commands.add_parser("post", help="Send one request; no automatic retry or key generation")
    post.add_argument("path")
    post.add_argument("--body-file", required=True, help="UTF-8 JSON object file; use {} for empty bodies")
    post.add_argument("--key-file", help="Existing intent-specific key file; required except for admission")
    wait = commands.add_parser("wait", help="Poll no faster than every 5 seconds and honor Retry-After; does not wait for resource RUNNING")
    wait.add_argument("operation_id")
    wait.add_argument("--timeout", type=float, default=300, help="Finite total polling window in seconds (default: 300)")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if not 0 < args.request_timeout < float("inf"):
            raise ValueError("--request-timeout must be positive and finite.")
        schema = args.command == "schema"
        method = "POST" if args.command == "post" else "GET"
        if args.command == "wait":
            if not re.fullmatch(r"[a-z0-9]{25}", args.operation_id):
                raise ValueError("Use the operation_id returned by the API (25 lowercase alphanumeric characters).")
            if not 0 < args.timeout < float("inf"):
                raise ValueError("--timeout must be positive and finite.")
            target = "/pt/api/operations/" + args.operation_id
        else:
            target = "/pt/api/openapi.json" if schema else args.path
        url = checked_url(args.base_url, target, method, schema)
        path = urlsplit(url).path
        key_file = getattr(args, "key_file", None)
        key_required = (method == "POST" and not path.endswith("/admission")) or path == "/pt/api/operations/by-key"
        if key_required and not key_file:
            raise ValueError("This request requires --key-file containing the original intent-specific key.")
        if key_file and method == "GET" and path != "/pt/api/operations/by-key":
            raise ValueError("GET --key-file is only supported for /pt/api/operations/by-key.")
        key = read_key(key_file) if key_file else None
        token = None if schema else read_token(args.token_file)
        body = read_body(args.body_file) if method == "POST" else None
        handlers = [NoRedirect()]
        if args.direct:
            handlers.append(ProxyHandler({}))
        opener = build_opener(*handlers)
        if args.command == "wait":
            return wait_operation(opener, url, token, args.timeout, args.request_timeout)
        status, response, retry_after = request(opener, method, url, token, key, body, args.request_timeout)
        return output_response(status, response, retry_after)
    except (URLError, TimeoutError, ConnectionError, HTTPException) as exc:
        print(f"Transport failure ({type(exc).__name__}): {exc}; no automatic retry.", file=sys.stderr)
        if args.command == "post":
            print("The response may be lost. Keep the original key; use get /pt/api/operations/by-key --key-file <same-file> before deciding whether to retry. Admission has no durable operation.", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
