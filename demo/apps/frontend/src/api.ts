import { Client, ClientOptions, Message } from "telepact";

export interface Todo {
  id: string;
  title: string;
  description: string;
  project: string;
  priority: string;
  dueDate: string | null;
  tags: string[];
  estimateMinutes: number;
  completed: boolean;
  completedAt: string | null;
  focusScore: number;
  focusLane: string;
  plannerReason: string;
  createdAt: string;
  updatedAt: string;
}

export interface PlannerTodoCard {
  id: string;
  title: string;
  project: string;
  priority: string;
  dueDate: string | null;
  estimateMinutes: number;
  focusScore: number;
  focusLane: string;
  plannerReason: string;
}

export interface FocusLaneGroup {
  lane: string;
  label: string;
  accent: string;
  todos: PlannerTodoCard[];
}

export interface ProjectSnapshot {
  project: string;
  openCount: number;
  completedCount: number;
  criticalCount: number;
}

export interface DashboardSummary {
  openCount: number;
  completedCount: number;
  overdueCount: number;
  todayCount: number;
  totalEstimatedMinutes: number;
}

export interface FocusSession {
  id: string;
  todoId: string;
  title: string;
  project: string;
  lane: string;
  minutes: number;
  startedAt: string;
  finishedAt: string;
}

export interface PlannerDashboard {
  generatedAt: string;
  summary: DashboardSummary;
  lanes: FocusLaneGroup[];
  projectSnapshots: ProjectSnapshot[];
  recentSessions: FocusSession[];
}

export interface HomeData {
  todos: Todo[];
  dashboard: PlannerDashboard;
}

export interface TodoMutationInput {
  title: string;
  description: string;
  project: string;
  priority: string;
  dueDate: string | null;
  tags: string[];
  estimateMinutes: number;
}

export interface TodoFilters {
  status: string;
  search: string;
  project: string;
  tag: string;
}

export class ApiError extends Error {
  constructor(
    readonly target: string,
    readonly payload: Record<string, unknown>,
  ) {
    super(target);
  }
}

const options = new ClientOptions();
options.alwaysSendJson = true;

const client = new Client(async (message, serializer) => {
  const response = await fetch("/api", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: serializer.serialize(message),
  });
  const bytes = new Uint8Array(await response.arrayBuffer());
  return serializer.deserialize(bytes);
}, options);

async function ok<T>(body: Record<string, unknown>): Promise<T> {
  const response = await client.request(new Message({}, body));
  if (response.getBodyTarget() !== "Ok_") {
    throw new ApiError(response.getBodyTarget(), response.getBodyPayload());
  }
  return response.getBodyPayload() as T;
}

export async function getHomeData(): Promise<HomeData> {
  const payload = await ok<{ home: HomeData }>({ "fn.getHomeData": {} });
  return payload.home;
}

export async function listTodos(filters: TodoFilters): Promise<Todo[]> {
  const payload = await ok<{ todos: Todo[] }>({ "fn.listTodos": filters });
  return payload.todos;
}

export async function createTodo(input: TodoMutationInput): Promise<Todo> {
  const payload = await ok<{ todo: Todo }>({
    "fn.createTodo": {
      ...input,
      dueDate: input.dueDate ?? "",
    },
  });
  return payload.todo;
}

export async function updateTodo(id: string, input: TodoMutationInput): Promise<Todo> {
  const payload = await ok<{ todo: Todo }>({
    "fn.updateTodo": {
      id,
      ...input,
      dueDate: input.dueDate ?? "",
    },
  });
  return payload.todo;
}

export async function toggleTodoCompletion(id: string, completed: boolean): Promise<Todo> {
  const payload = await ok<{ todo: Todo }>({ "fn.toggleTodoCompletion": { id, completed } });
  return payload.todo;
}

export async function deleteTodo(id: string): Promise<void> {
  await ok({ "fn.deleteTodo": { id } });
}

export async function startFocusSession(todoId: string, minutes: number): Promise<{
  session: FocusSession;
  dashboard: PlannerDashboard;
}> {
  return ok({ "fn.startFocusSession": { todoId, minutes } });
}
