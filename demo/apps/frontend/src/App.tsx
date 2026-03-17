import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";
import {
  ApiError,
  type HomeData,
  type PlannerDashboard,
  type Todo,
  createTodo,
  deleteTodo,
  getHomeData,
  listTodos,
  startFocusSession,
  toggleTodoCompletion,
  updateTodo,
} from "./api";

interface TodoDraft {
  title: string;
  description: string;
  project: string;
  priority: string;
  dueDate: string;
  tagsText: string;
  estimateMinutes: string;
}

const defaultDraft: TodoDraft = {
  title: "",
  description: "",
  project: "Inbox",
  priority: "medium",
  dueDate: "",
  tagsText: "",
  estimateMinutes: "30",
};

function toDraft(todo: Todo): TodoDraft {
  return {
    title: todo.title,
    description: todo.description,
    project: todo.project,
    priority: todo.priority,
    dueDate: todo.dueDate ?? "",
    tagsText: todo.tags.join(", "),
    estimateMinutes: String(todo.estimateMinutes),
  };
}

function toInput(draft: TodoDraft) {
  return {
    title: draft.title.trim(),
    description: draft.description.trim(),
    project: draft.project.trim() || "Inbox",
    priority: draft.priority,
    dueDate: draft.dueDate.trim() || null,
    tags: draft.tagsText
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean),
    estimateMinutes: Number.parseInt(draft.estimateMinutes || "30", 10),
  };
}

function relativeLaneTone(lane: string): string {
  switch (lane) {
    case "overdue":
      return "lane-overdue";
    case "today":
      return "lane-today";
    case "soon":
      return "lane-soon";
    default:
      return "lane-backlog";
  }
}

export function App() {
  const [home, setHome] = useState<HomeData | null>(null);
  const [todos, setTodos] = useState<Todo[]>([]);
  const [filters, setFilters] = useState({
    status: "all",
    search: "",
    project: "",
    tag: "",
  });
  const [draft, setDraft] = useState<TodoDraft>(defaultDraft);
  const [editingTodoId, setEditingTodoId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const deferredSearch = useDeferredValue(filters.search);

  const projects = useMemo(() => {
    const source = home?.todos ?? [];
    return [...new Set(source.map((todo) => todo.project))].sort();
  }, [home]);

  async function refreshHome(): Promise<HomeData> {
    const nextHome = await getHomeData();
    startTransition(() => {
      setHome(nextHome);
    });
    return nextHome;
  }

  async function refreshTodos() {
    const nextTodos = await listTodos({
      ...filters,
      search: deferredSearch,
    });
    startTransition(() => {
      setTodos(nextTodos);
    });
  }

  async function refreshAll() {
    const nextHome = await refreshHome();
    const nextTodos = await listTodos({
      ...filters,
      search: deferredSearch,
    });
    startTransition(() => {
      setHome(nextHome);
      setTodos(nextTodos);
    });
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const nextHome = await getHomeData();
        const nextTodos = await listTodos({
          status: "all",
          search: "",
          project: "",
          tag: "",
        });
        if (cancelled) {
          return;
        }
        setHome(nextHome);
        setTodos(nextTodos);
        setError(null);
      } catch (cause) {
        if (!cancelled) {
          setError(formatError(cause));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!home) {
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const nextTodos = await listTodos({
          ...filters,
          search: deferredSearch,
        });
        if (!cancelled) {
          setTodos(nextTodos);
        }
      } catch (cause) {
        if (!cancelled) {
          setError(formatError(cause));
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [deferredSearch, filters.project, filters.status, filters.tag, home]);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    try {
      const input = toInput(draft);
      if (editingTodoId) {
        await updateTodo(editingTodoId, input);
      } else {
        await createTodo(input);
      }
      await refreshAll();
      setDraft(defaultDraft);
      setEditingTodoId(null);
      setError(null);
    } catch (cause) {
      setError(formatError(cause));
    } finally {
      setBusy(false);
    }
  }

  async function onToggle(todo: Todo) {
    setBusy(true);
    try {
      await toggleTodoCompletion(todo.id, !todo.completed);
      await refreshAll();
      setError(null);
    } catch (cause) {
      setError(formatError(cause));
    } finally {
      setBusy(false);
    }
  }

  async function onDelete(todo: Todo) {
    setBusy(true);
    try {
      await deleteTodo(todo.id);
      await refreshAll();
      setError(null);
    } catch (cause) {
      setError(formatError(cause));
    } finally {
      setBusy(false);
    }
  }

  async function onStartFocus(todoId: string) {
    setBusy(true);
    try {
      const result = await startFocusSession(todoId, 25);
      setHome((current) => current ? { ...current, dashboard: result.dashboard } : current);
      setError(null);
    } catch (cause) {
      setError(formatError(cause));
    } finally {
      setBusy(false);
    }
  }

  function startEditing(todo: Todo) {
    setEditingTodoId(todo.id);
    setDraft(toDraft(todo));
  }

  function cancelEditing() {
    setEditingTodoId(null);
    setDraft(defaultDraft);
  }

  const dashboard: PlannerDashboard | null = home?.dashboard ?? null;

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Telepact Full-Stack Demo</p>
          <h1>Todo workbench with a Python task core, a Java planning engine, and a thin TypeScript BFF.</h1>
          <p className="lede">
            The browser speaks Telepact to the BFF, the BFF mostly proxies to the backend services,
            and the planner service uses a Telepact field projection when it fetches todos.
          </p>
        </div>
        <button className="refreshButton" onClick={() => void refreshAll()} disabled={busy || loading}>
          Refresh snapshot
        </button>
      </section>

      {error ? <div className="errorBanner">{error}</div> : null}

      {loading || !dashboard ? (
        <div className="loadingCard">Loading the workspace…</div>
      ) : (
        <>
          <section className="summaryGrid">
            <SummaryCard label="Open" value={dashboard.summary.openCount} />
            <SummaryCard label="Completed" value={dashboard.summary.completedCount} />
            <SummaryCard label="Overdue" value={dashboard.summary.overdueCount} />
            <SummaryCard label="Today" value={dashboard.summary.todayCount} />
            <SummaryCard label="Est. Minutes" value={dashboard.summary.totalEstimatedMinutes} />
          </section>

          <section className="contentGrid">
            <div className="column">
              <section className="panel">
                <div className="panelHeader">
                  <div>
                    <p className="eyebrow">Composer</p>
                    <h2>{editingTodoId ? "Refine the selected task" : "Capture the next piece of work"}</h2>
                  </div>
                  {editingTodoId ? (
                    <button className="ghostButton" onClick={cancelEditing} type="button">
                      Cancel edit
                    </button>
                  ) : null}
                </div>
                <form className="todoForm" onSubmit={onSubmit}>
                  <label>
                    Title
                    <input
                      value={draft.title}
                      onChange={(event) => setDraft((current) => ({ ...current, title: event.target.value }))}
                      placeholder="Draft the release retrospective"
                      required
                    />
                  </label>
                  <label>
                    Description
                    <textarea
                      value={draft.description}
                      onChange={(event) => setDraft((current) => ({ ...current, description: event.target.value }))}
                      placeholder="Capture the context, constraints, and expected outcome."
                      rows={4}
                    />
                  </label>
                  <div className="formRow">
                    <label>
                      Project
                      <input
                        value={draft.project}
                        onChange={(event) => setDraft((current) => ({ ...current, project: event.target.value }))}
                      />
                    </label>
                    <label>
                      Priority
                      <select
                        value={draft.priority}
                        onChange={(event) => setDraft((current) => ({ ...current, priority: event.target.value }))}
                      >
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                      </select>
                    </label>
                  </div>
                  <div className="formRow">
                    <label>
                      Due date
                      <input
                        type="date"
                        value={draft.dueDate}
                        onChange={(event) => setDraft((current) => ({ ...current, dueDate: event.target.value }))}
                      />
                    </label>
                    <label>
                      Estimate (minutes)
                      <input
                        type="number"
                        min="5"
                        step="5"
                        value={draft.estimateMinutes}
                        onChange={(event) =>
                          setDraft((current) => ({ ...current, estimateMinutes: event.target.value }))
                        }
                      />
                    </label>
                  </div>
                  <label>
                    Tags
                    <input
                      value={draft.tagsText}
                      onChange={(event) => setDraft((current) => ({ ...current, tagsText: event.target.value }))}
                      placeholder="launch, finance, research"
                    />
                  </label>
                  <button className="primaryButton" disabled={busy} type="submit">
                    {editingTodoId ? "Save task" : "Add task"}
                  </button>
                </form>
              </section>

              <section className="panel">
                <div className="panelHeader">
                  <div>
                    <p className="eyebrow">Task List</p>
                    <h2>Track the work from backlog through done.</h2>
                  </div>
                </div>
                <div className="filterRow">
                  <input
                    aria-label="Search tasks"
                    placeholder="Search by title, project, or tag"
                    value={filters.search}
                    onChange={(event) => setFilters((current) => ({ ...current, search: event.target.value }))}
                  />
                  <select
                    aria-label="Status filter"
                    value={filters.status}
                    onChange={(event) => setFilters((current) => ({ ...current, status: event.target.value }))}
                  >
                    <option value="all">All</option>
                    <option value="open">Open</option>
                    <option value="completed">Completed</option>
                  </select>
                  <select
                    aria-label="Project filter"
                    value={filters.project}
                    onChange={(event) => setFilters((current) => ({ ...current, project: event.target.value }))}
                  >
                    <option value="">All projects</option>
                    {projects.map((project) => (
                      <option key={project} value={project}>
                        {project}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="todoList">
                  {todos.map((todo) => (
                    <article key={todo.id} className={`todoCard ${todo.completed ? "todoDone" : ""}`}>
                      <div className="todoMain">
                        <div className={`laneChip ${relativeLaneTone(todo.focusLane)}`}>{todo.focusLane}</div>
                        <h3>{todo.title}</h3>
                        <p>{todo.description}</p>
                        <div className="metaRow">
                          <span>{todo.project}</span>
                          <span>{todo.priority}</span>
                          <span>{todo.estimateMinutes} min</span>
                          <span>Score {todo.focusScore}</span>
                          {todo.dueDate ? <span>Due {todo.dueDate}</span> : null}
                        </div>
                        <div className="tagRow">
                          {todo.tags.map((tag) => (
                            <span key={tag} className="tag">
                              {tag}
                            </span>
                          ))}
                        </div>
                        <p className="plannerReason">{todo.plannerReason}</p>
                      </div>
                      <div className="todoActions">
                        <button className="ghostButton" onClick={() => void onToggle(todo)} type="button">
                          {todo.completed ? "Re-open" : "Done"}
                        </button>
                        <button className="ghostButton" onClick={() => startEditing(todo)} type="button">
                          Edit
                        </button>
                        <button className="ghostButton dangerButton" onClick={() => void onDelete(todo)} type="button">
                          Delete
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            </div>

            <div className="column">
              <section className="panel plannerPanel">
                <div className="panelHeader">
                  <div>
                    <p className="eyebrow">Planner</p>
                    <h2>Java service digest of the todo graph.</h2>
                  </div>
                  <p className="timestamp">Updated {new Date(dashboard.generatedAt).toLocaleString()}</p>
                </div>
                <div className="laneStack">
                  {dashboard.lanes.map((lane) => (
                    <section key={lane.lane} className="laneSection" style={{ borderColor: lane.accent }}>
                      <div className="laneHeader">
                        <h3>{lane.label}</h3>
                        <span>{lane.todos.length} items</span>
                      </div>
                      <div className="plannerCards">
                        {lane.todos.map((todo) => (
                          <article key={todo.id} className="plannerCard">
                            <div>
                              <h4>{todo.title}</h4>
                              <p>{todo.project}</p>
                              <p className="plannerReason">{todo.plannerReason}</p>
                            </div>
                            <div className="plannerMeta">
                              <span>{todo.priority}</span>
                              <span>{todo.estimateMinutes} min</span>
                              <span>Score {todo.focusScore}</span>
                              {todo.dueDate ? <span>{todo.dueDate}</span> : null}
                            </div>
                            <button className="primaryButton smallButton" onClick={() => void onStartFocus(todo.id)}>
                              Start 25 min focus
                            </button>
                          </article>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              </section>

              <section className="panel">
                <div className="panelHeader">
                  <div>
                    <p className="eyebrow">Projects</p>
                    <h2>Cross-project pressure snapshot.</h2>
                  </div>
                </div>
                <div className="projectGrid">
                  {dashboard.projectSnapshots.map((snapshot) => (
                    <article key={snapshot.project} className="projectCard">
                      <h3>{snapshot.project}</h3>
                      <div className="projectStats">
                        <span>{snapshot.openCount} open</span>
                        <span>{snapshot.completedCount} completed</span>
                        <span>{snapshot.criticalCount} critical</span>
                      </div>
                    </article>
                  ))}
                </div>
              </section>

              <section className="panel">
                <div className="panelHeader">
                  <div>
                    <p className="eyebrow">Recent Focus</p>
                    <h2>Sessions captured by the planner service.</h2>
                  </div>
                </div>
                <div className="sessionList">
                  {dashboard.recentSessions.length === 0 ? (
                    <p className="emptyState">Start a focus session from the planner lane cards to populate this area.</p>
                  ) : (
                    dashboard.recentSessions.map((session) => (
                      <article key={session.id} className="sessionCard">
                        <h3>{session.title}</h3>
                        <p>{session.project}</p>
                        <div className="projectStats">
                          <span>{session.minutes} min</span>
                          <span>{session.lane}</span>
                          <span>{new Date(session.startedAt).toLocaleTimeString()}</span>
                        </div>
                      </article>
                    ))
                  )}
                </div>
              </section>
            </div>
          </section>
        </>
      )}
    </main>
  );
}

function SummaryCard(props: { label: string; value: number }) {
  return (
    <article className="summaryCard">
      <p>{props.label}</p>
      <h2>{props.value}</h2>
    </article>
  );
}

function formatError(cause: unknown): string {
  if (cause instanceof ApiError) {
    if (cause.target === "ErrorTodoNotFound") {
      return "The selected todo could not be found.";
    }
    return `${cause.target}: ${JSON.stringify(cause.payload)}`;
  }
  if (cause instanceof Error) {
    return cause.message;
  }
  return "Unexpected error";
}
