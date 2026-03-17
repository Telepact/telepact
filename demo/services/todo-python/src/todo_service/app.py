from __future__ import annotations

import os
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Request, Response
from telepact import Client, Message, Server, TelepactSchema


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def date_to_iso(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def parse_due_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def normalize_due_date(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def default_schema_dir() -> str:
    return str(Path(__file__).resolve().parents[4] / "schemas" / "todo")


def seed_todos() -> list[dict[str, Any]]:
    today = date.today()
    now = iso_now()
    return [
        {
            "id": "todo-launch-polish",
            "title": "Polish onboarding copy",
            "description": "Tighten the first-run checklist before the stakeholder review.",
            "project": "Launch",
            "priority": "critical",
            "dueDate": date_to_iso(today),
            "tags": ["copy", "launch"],
            "estimateMinutes": 45,
            "completed": False,
            "completedAt": None,
            "focusScore": 96,
            "focusLane": "today",
            "plannerReason": "Critical task due today with a short estimated duration.",
            "createdAt": now,
            "updatedAt": now,
        },
        {
            "id": "todo-tax-forms",
            "title": "Upload vendor tax forms",
            "description": "Collect W-9s from the remaining two suppliers.",
            "project": "Operations",
            "priority": "high",
            "dueDate": date_to_iso(today - timedelta(days=1)),
            "tags": ["finance"],
            "estimateMinutes": 30,
            "completed": False,
            "completedAt": None,
            "focusScore": 98,
            "focusLane": "overdue",
            "plannerReason": "Overdue work with a high-priority tag should be handled first.",
            "createdAt": now,
            "updatedAt": now,
        },
        {
            "id": "todo-beta-metrics",
            "title": "Review beta adoption metrics",
            "description": "Compare activation, retention, and conversion across cohorts.",
            "project": "Growth",
            "priority": "medium",
            "dueDate": date_to_iso(today + timedelta(days=2)),
            "tags": ["analytics", "beta"],
            "estimateMinutes": 60,
            "completed": False,
            "completedAt": None,
            "focusScore": 74,
            "focusLane": "soon",
            "plannerReason": "Upcoming deadline and strategic impact make this a near-term focus item.",
            "createdAt": now,
            "updatedAt": now,
        },
        {
            "id": "todo-ui-garden",
            "title": "Refactor design system tokens",
            "description": "Normalize semantic colors and card spacing across the app shell.",
            "project": "Design System",
            "priority": "medium",
            "dueDate": None,
            "tags": ["design", "frontend"],
            "estimateMinutes": 90,
            "completed": False,
            "completedAt": None,
            "focusScore": 58,
            "focusLane": "backlog",
            "plannerReason": "Important cleanup without a hard due date fits the backlog lane.",
            "createdAt": now,
            "updatedAt": now,
        },
        {
            "id": "todo-changelog",
            "title": "Ship beta changelog",
            "description": "Publish release notes and customer migration tips.",
            "project": "Launch",
            "priority": "high",
            "dueDate": date_to_iso(today - timedelta(days=2)),
            "tags": ["docs"],
            "estimateMinutes": 25,
            "completed": True,
            "completedAt": now,
            "focusScore": 88,
            "focusLane": "today",
            "plannerReason": "Completed work remains visible for dashboard context.",
            "createdAt": now,
            "updatedAt": now,
        },
    ]


class TodoStore:
    def __init__(self) -> None:
        self.todos = seed_todos()

    def list_todos(self, status: str, search: str, project: str, tag: str) -> list[dict[str, Any]]:
        normalized_search = search.strip().lower()
        normalized_project = project.strip().lower()
        normalized_tag = tag.strip().lower()
        filtered = []
        for todo in self.todos:
            if status == "open" and todo["completed"]:
                continue
            if status == "completed" and not todo["completed"]:
                continue
            if normalized_project and todo["project"].lower() != normalized_project:
                continue
            if normalized_tag and normalized_tag not in [value.lower() for value in todo["tags"]]:
                continue
            haystack = " ".join(
                [todo["title"], todo["description"], todo["project"], " ".join(todo["tags"])]
            ).lower()
            if normalized_search and normalized_search not in haystack:
                continue
            filtered.append(todo.copy())
        filtered.sort(key=lambda item: (item["completed"], -item["focusScore"], item["title"]))
        return filtered

    def get(self, todo_id: str) -> dict[str, Any] | None:
        for todo in self.todos:
            if todo["id"] == todo_id:
                return todo
        return None

    def create(self, payload: dict[str, Any], enrichment: dict[str, Any]) -> dict[str, Any]:
        now = iso_now()
        todo = {
            "id": f"todo-{uuid.uuid4().hex[:10]}",
            "title": payload["title"].strip(),
            "description": payload["description"].strip(),
            "project": payload["project"].strip() or "Inbox",
            "priority": payload["priority"],
            "dueDate": normalize_due_date(payload["dueDate"]),
            "tags": payload["tags"],
            "estimateMinutes": payload["estimateMinutes"],
            "completed": False,
            "completedAt": None,
            "focusScore": enrichment["score"],
            "focusLane": enrichment["lane"],
            "plannerReason": enrichment["reason"],
            "createdAt": now,
            "updatedAt": now,
        }
        self.todos.append(todo)
        return todo.copy()

    def update(self, payload: dict[str, Any], enrichment: dict[str, Any]) -> dict[str, Any] | None:
        todo = self.get(payload["id"])
        if todo is None:
            return None
        todo.update(
            {
                "title": payload["title"].strip(),
                "description": payload["description"].strip(),
                "project": payload["project"].strip() or "Inbox",
                "priority": payload["priority"],
                "dueDate": normalize_due_date(payload["dueDate"]),
                "tags": payload["tags"],
                "estimateMinutes": payload["estimateMinutes"],
                "focusScore": enrichment["score"],
                "focusLane": enrichment["lane"],
                "plannerReason": enrichment["reason"],
                "updatedAt": iso_now(),
            }
        )
        return todo.copy()

    def toggle(self, todo_id: str, completed: bool) -> dict[str, Any] | None:
        todo = self.get(todo_id)
        if todo is None:
            return None
        todo["completed"] = completed
        todo["completedAt"] = iso_now() if completed else None
        todo["updatedAt"] = iso_now()
        return todo.copy()

    def delete(self, todo_id: str) -> bool:
        before = len(self.todos)
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        return len(self.todos) != before


class PlannerClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.http_client = httpx.AsyncClient(timeout=5.0)
        options = Client.Options()
        options.always_send_json = True

        async def adapter(message: Message, serializer: Any) -> Message:
            response = await self.http_client.post(
                self.base_url,
                content=serializer.serialize(message),
                headers={"content-type": "application/json"},
            )
            response.raise_for_status()
            return serializer.deserialize(response.content)

        self.client = Client(adapter, options)

    async def score_draft(self, payload: dict[str, Any]) -> dict[str, Any]:
        message = await self.client.request(
            Message(
                {},
                {
                    "fn.scoreTodoDraft": {
                        "title": payload["title"],
                        "description": payload["description"],
                        "project": payload["project"],
                        "priority": payload["priority"],
                        "dueDate": normalize_due_date(payload["dueDate"]),
                        "tags": payload["tags"],
                        "estimateMinutes": payload["estimateMinutes"],
                    }
                },
            )
        )
        if message.get_body_target() != "Ok_":
            raise RuntimeError(f"Planner scoring failed: {message.body}")
        return message.get_body_payload()

    async def close(self) -> None:
        await self.http_client.aclose()


@dataclass
class TodoServiceContext:
    store: TodoStore
    planner_client: PlannerClient
    server: Server


def create_context(
    schema_dir: str | None = None,
    planner_service_url: str | None = None,
) -> TodoServiceContext:
    resolved_schema_dir = schema_dir or os.getenv("SCHEMA_DIR", default_schema_dir())
    resolved_planner_service_url = planner_service_url or os.getenv(
        "PLANNER_SERVICE_URL", "http://127.0.0.1:7002/api"
    )
    schema = TelepactSchema.from_directory(resolved_schema_dir)
    store = TodoStore()
    planner_client = PlannerClient(resolved_planner_service_url)

    async def handler(request_message: Message) -> Message:
        function_name = request_message.get_body_target()
        payload = request_message.get_body_payload()

        try:
            if function_name == "fn.listTodos":
                todos = store.list_todos(
                    payload["status"], payload["search"], payload["project"], payload["tag"]
                )
                return Message({}, {"Ok_": {"todos": todos}})

            if function_name == "fn.createTodo":
                enrichment = await planner_client.score_draft(payload)
                todo = store.create(payload, enrichment)
                return Message({}, {"Ok_": {"todo": todo}})

            if function_name == "fn.updateTodo":
                enrichment = await planner_client.score_draft(payload)
                todo = store.update(payload, enrichment)
                if todo is None:
                    return Message({}, {"ErrorTodoNotFound": {"id": payload["id"]}})
                return Message({}, {"Ok_": {"todo": todo}})

            if function_name == "fn.toggleTodoCompletion":
                todo = store.toggle(payload["id"], payload["completed"])
                if todo is None:
                    return Message({}, {"ErrorTodoNotFound": {"id": payload["id"]}})
                return Message({}, {"Ok_": {"todo": todo}})

            if function_name == "fn.deleteTodo":
                deleted = store.delete(payload["id"])
                if not deleted:
                    return Message({}, {"ErrorTodoNotFound": {"id": payload["id"]}})
                return Message({}, {"Ok_": {}})

            return Message({}, {"ErrorInternal": {"message": f"Unknown function {function_name}"}})
        except Exception as exc:  # pragma: no cover - defensive mapping for Telepact responses
            return Message({}, {"ErrorInternal": {"message": str(exc)}})

    options = Server.Options()
    options.auth_required = False
    server = Server(schema, handler, options)
    return TodoServiceContext(store=store, planner_client=planner_client, server=server)


def create_app(
    schema_dir: str | None = None,
    planner_service_url: str | None = None,
) -> FastAPI:
    context = create_context(schema_dir=schema_dir, planner_service_url=planner_service_url)

    @asynccontextmanager
    async def lifespan(_application: FastAPI):
        _application.state.todo_context = context
        yield
        await context.planner_client.close()

    application = FastAPI(title="Telepact Demo Todo Service", lifespan=lifespan)

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/api")
    async def api_endpoint(request: Request) -> Response:
        body = await request.body()
        result = await context.server.process(body)
        headers = {key: str(value) for key, value in result.headers.items()}
        return Response(content=result.bytes, media_type="application/json", headers=headers)

    return application


app = create_app()
