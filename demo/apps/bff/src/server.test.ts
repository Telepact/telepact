import path from "node:path";
import { spawn, type ChildProcess } from "node:child_process";
import net from "node:net";
import { afterEach, describe, expect, test } from "vitest";
import request from "supertest";
import { createApp } from "./server.js";
import { resolveDemoRoot } from "./config.js";

const demoRoot = resolveDemoRoot();
const telepactCli = path.join(demoRoot, ".venv", "bin", "telepact");

interface MockServer {
  process: ChildProcess;
  url: string;
}

let nextPort = 19100;

async function reservePort(): Promise<number> {
  const port = nextPort;
  nextPort += 1;
  return port;
}

async function waitForPort(port: number): Promise<void> {
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    const connected = await new Promise<boolean>((resolve) => {
      const socket = net.createConnection({ host: "127.0.0.1", port }, () => {
        socket.end();
        resolve(true);
      });
      socket.on("error", () => resolve(false));
    });
    if (connected) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Timed out waiting for port ${port}`);
}

async function startMock(schemaName: string): Promise<MockServer> {
  const port = await reservePort();
  const process = spawn(
    telepactCli,
    ["mock", "--dir", path.join(demoRoot, "schemas", schemaName), "--port", String(port)],
    {
      cwd: demoRoot,
      stdio: "ignore",
    },
  );
  await waitForPort(port);
  return { process, url: `http://127.0.0.1:${port}/api` };
}

async function wireCall(url: string, body: Record<string, unknown>, headers: Record<string, unknown> = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify([headers, body]),
  });
  return JSON.parse(await response.text()) as [Record<string, unknown>, Record<string, unknown>];
}

const startedProcesses: ChildProcess[] = [];

afterEach(() => {
  for (const process of startedProcesses.splice(0)) {
    process.kill();
  }
});

describe("BFF Telepact API", () => {
  test("getHomeData fans out to todo and planner services", async () => {
    const todoMock = await startMock("todo");
    const plannerMock = await startMock("planner");
    startedProcesses.push(todoMock.process, plannerMock.process);

    await wireCall(todoMock.url, {
      "fn.createStub_": {
        stub: {
          "fn.listTodos": {
            status: "all",
            search: "",
            project: "",
            tag: "",
          },
          "->": {
            Ok_: {
              todos: [
                {
                  id: "todo-1",
                  title: "Write launch brief",
                  description: "Draft the executive summary.",
                  project: "Launch",
                  priority: "high",
                  dueDate: "2030-01-20",
                  tags: ["launch"],
                  estimateMinutes: 45,
                  completed: false,
                  completedAt: null,
                  focusScore: 88,
                  focusLane: "today",
                  plannerReason: "Priority and due date make this a today task.",
                  createdAt: "2030-01-18T10:00:00Z",
                  updatedAt: "2030-01-18T10:00:00Z",
                },
              ],
            },
          },
        },
      },
    });

    await wireCall(plannerMock.url, {
      "fn.createStub_": {
        stub: {
          "fn.getPlannerDashboard": {},
          "->": {
            Ok_: {
              dashboard: {
                generatedAt: "2030-01-18T10:05:00Z",
                summary: {
                  openCount: 1,
                  completedCount: 0,
                  overdueCount: 0,
                  todayCount: 1,
                  totalEstimatedMinutes: 45,
                },
                lanes: [
                  {
                    lane: "today",
                    label: "Today",
                    accent: "#d96f32",
                    todos: [
                      {
                        id: "todo-1",
                        title: "Write launch brief",
                        project: "Launch",
                        priority: "high",
                        dueDate: "2030-01-20",
                        estimateMinutes: 45,
                        focusScore: 88,
                        focusLane: "today",
                        plannerReason: "Priority and due date make this a today task.",
                      },
                    ],
                  },
                ],
                projectSnapshots: [
                  {
                    project: "Launch",
                    openCount: 1,
                    completedCount: 0,
                    criticalCount: 0,
                  },
                ],
                recentSessions: [],
              },
            },
          },
        },
      },
    });

    const app = createApp({
      demoRoot,
      port: 3000,
      browserSchemaDir: path.join(demoRoot, "schemas", "browser"),
      staticDir: path.join(demoRoot, "apps", "bff", "static"),
      todoServiceUrl: todoMock.url,
      plannerServiceUrl: plannerMock.url,
    });

    const response = await request(app)
      .post("/api")
      .set("content-type", "application/json")
      .send(JSON.stringify([{}, { "fn.getHomeData": {} }]));

    const payload = JSON.parse(response.text);
    expect(payload[1].Ok_.home.todos).toHaveLength(1);
    expect(payload[1].Ok_.home.dashboard.summary.openCount).toBe(1);

    const todoVerification = await wireCall(todoMock.url, {
      "fn.verify_": {
        call: {
          "fn.listTodos": {
            status: "all",
            search: "",
            project: "",
            tag: "",
          },
        },
      },
    });
    expect(todoVerification[1]).toEqual({ Ok_: {} });

    const plannerVerification = await wireCall(plannerMock.url, {
      "fn.verify_": {
        call: {
          "fn.getPlannerDashboard": {},
        },
      },
    });
    expect(plannerVerification[1]).toEqual({ Ok_: {} });
  });

  test("toggleTodoCompletion passes through domain errors", async () => {
    const todoMock = await startMock("todo");
    const plannerMock = await startMock("planner");
    startedProcesses.push(todoMock.process, plannerMock.process);

    await wireCall(todoMock.url, {
      "fn.createStub_": {
        stub: {
          "fn.toggleTodoCompletion": {
            id: "missing",
            completed: true,
          },
          "->": {
            ErrorTodoNotFound: {
              id: "missing",
            },
          },
        },
      },
    });

    const app = createApp({
      demoRoot,
      port: 3000,
      browserSchemaDir: path.join(demoRoot, "schemas", "browser"),
      staticDir: path.join(demoRoot, "apps", "bff", "static"),
      todoServiceUrl: todoMock.url,
      plannerServiceUrl: plannerMock.url,
    });

    const response = await request(app)
      .post("/api")
      .set("content-type", "application/json")
      .send(JSON.stringify([{}, { "fn.toggleTodoCompletion": { id: "missing", completed: true } }]));

    const payload = JSON.parse(response.text);
    expect(payload[1]).toEqual({ ErrorTodoNotFound: { id: "missing" } });
  });
});
