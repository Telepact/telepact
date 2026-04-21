import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import click

GITHUB_API_ROOT = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise click.ClickException(f"{name} environment variable is not set.")
    return value


def write_github_outputs(path: Path | None, outputs: dict[str, Any]) -> None:
    if path is None:
        return

    lines = []
    for key, value in outputs.items():
        rendered = "true" if value is True else "false" if value is False else str(value)
        lines.append(f"{key}={rendered}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def github_rest_request(
    token: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    expected_statuses: tuple[int, ...] = (200,),
) -> tuple[int, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{GITHUB_API_ROOT}/{path.lstrip('/')}",
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            **({"Content-Type": "application/json"} if payload is not None else {}),
        },
    )

    try:
        with urlopen(request) as response:
            status = response.status
            raw_body = response.read().decode("utf-8")
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8")
        try:
            data = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            data = {}
        message = data.get("message") if isinstance(data, dict) else None
        raise click.ClickException(message or f"GitHub API request failed: {exc.code} {exc.reason}") from exc

    if status not in expected_statuses:
        raise click.ClickException(f"GitHub API request returned unexpected status {status} for {method} {path}")

    if not raw_body:
        return status, None

    try:
        return status, json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"GitHub API returned invalid JSON for {method} {path}") from exc
