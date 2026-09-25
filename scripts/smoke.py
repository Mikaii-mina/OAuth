#!/usr/bin/env python3
"""Check baseline availability and unauthenticated OAuth defenses."""

import argparse
from html.parser import HTMLParser
import json
import ssl
import time
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener


class LoginLink(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if "/oauth/authorize?" in href:
                self.href = href


def check(number: str, timeout: int, health_only: bool = False) -> None:
    server = f"https://server-{number}.oauth.labs"
    client = f"https://client-{number}.oauth.labs"
    opener = build_opener(ProxyHandler({}), HTTPSHandler(context=ssl._create_unverified_context()))

    def fetch(url):
        with opener.open(Request(url), timeout=5) as response:
            return response.status, response.read().decode("utf-8")

    deadline = time.monotonic() + timeout
    while True:
        try:
            for host in (server, client):
                status, body = fetch(host + "/health")
                if status != 200 or json.loads(body).get("status") != "healthy":
                    raise RuntimeError(f"{host} unhealthy: {body}")
            break
        except Exception:
            if time.monotonic() >= deadline:
                raise
            time.sleep(2)

    if health_only:
        print(f"lab{number}: healthy")
        return

    status, body = fetch(client + "/login")
    link = LoginLink()
    link.feed(body)
    if status != 200 or not link.href:
        raise AssertionError("client login page has no authorization link")
    authorization = urlparse(link.href)
    params = parse_qs(authorization.query)
    if (authorization.scheme, authorization.netloc, authorization.path) != (
        "https", f"server-{number}.oauth.labs", "/oauth/authorize"
    ):
        raise AssertionError(f"unexpected authorization endpoint: {authorization.geturl()}")
    for key in ("state", "code_challenge", "client_id", "redirect_uri"):
        if not params.get(key):
            raise AssertionError(f"authorization request missing {key}")
    if params.get("code_challenge_method") != ["S256"]:
        raise AssertionError("PKCE must use S256")
    if params.get("redirect_uri") != [client + "/callback"]:
        raise AssertionError("unexpected redirect URI")
    try:
        fetch(client + "/callback?code=fake&state=fake")
    except HTTPError as error:
        if error.code != 400 or b"Invalid state" not in error.read():
            raise AssertionError("callback did not reject wrong state") from error
    else:
        raise AssertionError("callback accepted wrong state")
    print(f"lab{number}: healthy, state and S256 PKCE present, invalid state rejected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", default="00", choices=[f"{n:02d}" for n in range(100)])
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--health-only", action="store_true")
    options = parser.parse_args()
    check(options.lab, options.timeout, options.health_only)
