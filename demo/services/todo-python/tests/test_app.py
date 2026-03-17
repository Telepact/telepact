from __future__ import annotations

import asyncio
import json
import os
import signal
import socket
import subprocess
import time
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport

from todo_service.app import create_app


ROOT = Path(__file__).resolve().parents[3]
TELEPACT = ROOT / ".venv" / "bin" / "telepact"
NEXT_PORT = 19200


def reserve_port() -> int:
    global NEXT_PORT
    port = NEXT_PORT
    NEXT_PORT += 1
    return port


def wait_for_port(port: int) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f"Timed out waiting for port {port}")


async def telepact_post(client: httpx.AsyncClient, body: dict, headers: dict | None = None) -> list[dict]:
    response = await client.post(
        "/api",
        content=json.dumps([headers or {}, body]).encode(),
        headers={"content-type": "application/json"},
    )
    response.raise_for_status()
    return json.loads(response.content)


async def wire_post(url: str, body: dict, headers: dict | None = None) -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            url,
            content=json.dumps([headers or {}, body]).encode(),
            headers={"content-type": "application/json"},
        )
        response.raise_for_status()
        return json.loads(response.content)


@pytest.fixture()
def planner_mock() -> str:
    port = reserve_port()
    process = subprocess.Popen(
        [
            str(TELEPACT),
            "mock",
            "--dir",
            str(ROOT / "schemas" / "planner"),
            "--port",
            str(port),
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )
    wait_for_port(port)
    try:
        yield f"http://127.0.0.1:{port}/api"
    finally:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)


def test_create_todo_uses_planner_mock(planner_mock: str) -> None:
    async def scenario() -> None:
        await wire_post(
            planner_mock,
            {
                "fn.createStub_": {
                    "stub": {
                        "fn.scoreTodoDraft": {
                            "title": "Write investor update",
                            "description": "Summarize wins and risks from the week.",
                            "project": "Growth",
                            "priority": "high",
                            "dueDate": "2030-01-20",
                            "tags": ["finance"],
                            "estimateMinutes": 35,
                        },
                        "->": {
                            "Ok_": {
                                "score": 91,
                                "lane": "today",
                                "reason": "High-priority work with a near-term deadline should land in today's lane.",
                            }
                        },
                    }
                }
            },
        )

        app = create_app(
            schema_dir=str(ROOT / "schemas" / "todo"),
            planner_service_url=planner_mock,
        )
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            payload = await telepact_post(
                client,
                {
                    "fn.createTodo": {
                        "title": "Write investor update",
                        "description": "Summarize wins and risks from the week.",
                        "project": "Growth",
                        "priority": "high",
                        "dueDate": "2030-01-20",
                        "tags": ["finance"],
                        "estimateMinutes": 35,
                    }
                },
            )

        assert payload[1]["Ok_"]["todo"]["focusScore"] == 91
        assert payload[1]["Ok_"]["todo"]["focusLane"] == "today"

        verification = await wire_post(
            planner_mock,
            {
                "fn.verify_": {
                    "call": {
                        "fn.scoreTodoDraft": {
                            "title": "Write investor update",
                            "description": "Summarize wins and risks from the week.",
                            "project": "Growth",
                            "priority": "high",
                            "dueDate": "2030-01-20",
                            "tags": ["finance"],
                            "estimateMinutes": 35,
                        }
                    }
                }
            },
        )
        assert verification[1] == {"Ok_": {}}

    asyncio.run(scenario())


def test_toggle_missing_todo_returns_domain_error(planner_mock: str) -> None:
    async def scenario() -> None:
        app = create_app(
            schema_dir=str(ROOT / "schemas" / "todo"),
            planner_service_url=planner_mock,
        )
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            payload = await telepact_post(
                client,
                {"fn.toggleTodoCompletion": {"id": "missing", "completed": True}},
            )

        assert payload[1] == {"ErrorTodoNotFound": {"id": "missing"}}

    asyncio.run(scenario())
