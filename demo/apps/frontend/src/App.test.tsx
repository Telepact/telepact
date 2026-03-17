import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { App } from "./App";
import * as api from "./api";

vi.mock("./api", async () => {
  const actual = await vi.importActual<typeof import("./api")>("./api");
  return {
    ...actual,
    getHomeData: vi.fn(),
    listTodos: vi.fn(),
    createTodo: vi.fn(),
    updateTodo: vi.fn(),
    toggleTodoCompletion: vi.fn(),
    deleteTodo: vi.fn(),
    startFocusSession: vi.fn(),
  };
});

const homeFixture = {
  todos: [
    {
      id: "todo-1",
      title: "Draft launch brief",
      description: "Summarize the narrative for tomorrow's review.",
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
            title: "Draft launch brief",
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
};

describe("App", () => {
  beforeEach(() => {
    vi.mocked(api.getHomeData).mockResolvedValue(homeFixture);
    vi.mocked(api.listTodos).mockResolvedValue(homeFixture.todos);
    vi.mocked(api.startFocusSession).mockResolvedValue({
      session: {
        id: "focus-1",
        todoId: "todo-1",
        title: "Draft launch brief",
        project: "Launch",
        lane: "today",
        minutes: 25,
        startedAt: "2030-01-18T10:10:00Z",
        finishedAt: "2030-01-18T10:35:00Z",
      },
      dashboard: {
        ...homeFixture.dashboard,
        recentSessions: [
          {
            id: "focus-1",
            todoId: "todo-1",
            title: "Draft launch brief",
            project: "Launch",
            lane: "today",
            minutes: 25,
            startedAt: "2030-01-18T10:10:00Z",
            finishedAt: "2030-01-18T10:35:00Z",
          },
        ],
      },
    });
  });

  test("renders summary and task list from Telepact home data", async () => {
    render(<App />);

    await screen.findByRole("heading", { level: 3, name: "Draft launch brief" });
    expect(screen.getByText("Track the work from backlog through done.")).toBeInTheDocument();
    expect(screen.getByText("Java service digest of the todo graph.")).toBeInTheDocument();
    expect(screen.getByText("Cross-project pressure snapshot.")).toBeInTheDocument();
  });

  test("changing the status filter reloads todos", async () => {
    const user = userEvent.setup();
    render(<App />);

    await screen.findByRole("heading", { level: 3, name: "Draft launch brief" });
    await user.selectOptions(screen.getAllByLabelText("Status filter")[0], "completed");

    await waitFor(() => {
      expect(api.listTodos).toHaveBeenLastCalledWith({
        status: "completed",
        search: "",
        project: "",
        tag: "",
      });
    });
  });
});
