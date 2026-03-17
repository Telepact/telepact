package com.example.planner;

import io.github.telepact.Message;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class PlannerService {
    private final TelepactHttpClient todoClient;
    private final PlannerStore store;

    public PlannerService(String todoServiceUrl) {
        this.todoClient = new TelepactHttpClient(todoServiceUrl);
        this.store = new PlannerStore();
    }

    public Message handle(Message requestMessage) {
        String functionName = requestMessage.getBodyTarget();
        Map<String, Object> payload = requestMessage.getBodyPayload();
        try {
            return switch (functionName) {
                case "fn.scoreTodoDraft" -> new Message(Map.of(), Map.of("Ok_", scoreTodoDraft(payload)));
                case "fn.getPlannerDashboard" -> new Message(
                    Map.of(),
                    Map.of("Ok_", Map.of("dashboard", buildDashboard()))
                );
                case "fn.startFocusSession" -> startFocusSession(payload);
                default -> new Message(
                    Map.of(),
                    Map.of("ErrorInternal", Map.of("message", "Unknown function " + functionName))
                );
            };
        } catch (Exception exception) {
            return new Message(
                Map.of(),
                Map.of("ErrorInternal", Map.of("message", exception.getMessage()))
            );
        }
    }

    private Message startFocusSession(Map<String, Object> payload) {
        String todoId = asString(payload.get("todoId"));
        int minutes = asInteger(payload.get("minutes"));
        List<Map<String, Object>> todos = fetchProjectedTodos();
        Map<String, Object> todo = todos.stream()
            .filter(item -> todoId.equals(asString(item.get("id"))))
            .findFirst()
            .orElse(null);
        if (todo == null) {
            return new Message(Map.of(), Map.of("ErrorTodoNotFound", Map.of("id", todoId)));
        }

        OffsetDateTime startedAt = OffsetDateTime.now(ZoneOffset.UTC);
        OffsetDateTime finishedAt = startedAt.plusMinutes(minutes);
        Map<String, Object> session = new LinkedHashMap<>();
        session.put("id", "focus-" + startedAt.toEpochSecond());
        session.put("todoId", todoId);
        session.put("title", asString(todo.get("title")));
        session.put("project", asString(todo.get("project")));
        session.put("lane", asString(todo.get("focusLane")));
        session.put("minutes", minutes);
        session.put("startedAt", startedAt.toString());
        session.put("finishedAt", finishedAt.toString());
        this.store.addSession(session);

        Map<String, Object> okPayload = new LinkedHashMap<>();
        okPayload.put("session", session);
        okPayload.put("dashboard", buildDashboard());
        return new Message(Map.of(), Map.of("Ok_", okPayload));
    }

    private Map<String, Object> scoreTodoDraft(Map<String, Object> payload) {
        String priority = asString(payload.get("priority")).toLowerCase();
        int score = switch (priority) {
            case "critical" -> 88;
            case "high" -> 74;
            case "medium" -> 58;
            case "low" -> 42;
            default -> 50;
        };

        List<String> reasons = new ArrayList<>();
        LocalDate today = LocalDate.now();
        String dueDateRaw = asNullableString(payload.get("dueDate"));
        if (dueDateRaw != null) {
            LocalDate dueDate = LocalDate.parse(dueDateRaw);
            long daysUntilDue = ChronoUnit.DAYS.between(today, dueDate);
            if (daysUntilDue < 0) {
                score += 18;
                reasons.add("It is already overdue.");
            } else if (daysUntilDue == 0) {
                score += 14;
                reasons.add("It is due today.");
            } else if (daysUntilDue <= 2) {
                score += 9;
                reasons.add("It is due within the next two days.");
            } else if (daysUntilDue <= 7) {
                score += 4;
                reasons.add("It has a near-term deadline.");
            }
        }

        int estimateMinutes = asInteger(payload.get("estimateMinutes"));
        if (estimateMinutes <= 30) {
            score += 6;
            reasons.add("The scope is small enough for a quick win.");
        } else if (estimateMinutes <= 60) {
            score += 3;
            reasons.add("The work fits comfortably in a focused session.");
        } else if (estimateMinutes >= 120) {
            score -= 4;
            reasons.add("The larger estimate lowers its immediate fit.");
        }

        for (String tag : asStringList(payload.get("tags"))) {
            if (tag.equalsIgnoreCase("launch") || tag.equalsIgnoreCase("finance")) {
                score += 4;
                reasons.add("A high-leverage tag increases urgency.");
                break;
            }
        }

        score = Math.max(20, Math.min(99, score));
        String lane = determineLane(score, priority, dueDateRaw);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("score", score);
        result.put("lane", lane);
        result.put("reason", String.join(" ", reasons));
        return result;
    }

    private String determineLane(int score, String priority, String dueDateRaw) {
        if (dueDateRaw != null) {
            LocalDate dueDate = LocalDate.parse(dueDateRaw);
            long daysUntilDue = ChronoUnit.DAYS.between(LocalDate.now(), dueDate);
            if (daysUntilDue < 0) {
                return "overdue";
            }
            if (daysUntilDue == 0 || "critical".equals(priority)) {
                return "today";
            }
            if (daysUntilDue <= 3 || score >= 80) {
                return "soon";
            }
            return "backlog";
        }
        if ("critical".equals(priority) || score >= 82) {
            return "today";
        }
        if (score >= 68) {
            return "soon";
        }
        return "backlog";
    }

    private Map<String, Object> buildDashboard() {
        List<Map<String, Object>> todos = fetchProjectedTodos();
        List<Map<String, Object>> recentSessions = this.store.recentSessions();
        List<Map<String, Object>> openTodos = todos.stream()
            .filter(todo -> !asBoolean(todo.get("completed")))
            .toList();
        List<Map<String, Object>> completedTodos = todos.stream()
            .filter(todo -> asBoolean(todo.get("completed")))
            .toList();

        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("openCount", openTodos.size());
        summary.put("completedCount", completedTodos.size());
        summary.put("overdueCount", countOverdue(openTodos));
        summary.put("todayCount", countToday(openTodos));
        summary.put("totalEstimatedMinutes", openTodos.stream().mapToInt(todo -> asInteger(todo.get("estimateMinutes"))).sum());

        List<Map<String, Object>> lanes = buildLanes(openTodos);
        List<Map<String, Object>> projectSnapshots = buildProjectSnapshots(todos);

        Map<String, Object> dashboard = new LinkedHashMap<>();
        dashboard.put("generatedAt", OffsetDateTime.now(ZoneOffset.UTC).toString());
        dashboard.put("summary", summary);
        dashboard.put("lanes", lanes);
        dashboard.put("projectSnapshots", projectSnapshots);
        dashboard.put("recentSessions", recentSessions);
        return dashboard;
    }

    private int countOverdue(List<Map<String, Object>> todos) {
        LocalDate today = LocalDate.now();
        return (int) todos.stream()
            .filter(todo -> {
                String dueDateRaw = asNullableString(todo.get("dueDate"));
                return dueDateRaw != null && LocalDate.parse(dueDateRaw).isBefore(today);
            })
            .count();
    }

    private int countToday(List<Map<String, Object>> todos) {
        LocalDate today = LocalDate.now();
        return (int) todos.stream()
            .filter(todo -> {
                String dueDateRaw = asNullableString(todo.get("dueDate"));
                return dueDateRaw != null && LocalDate.parse(dueDateRaw).isEqual(today);
            })
            .count();
    }

    private List<Map<String, Object>> buildLanes(List<Map<String, Object>> openTodos) {
        Map<String, List<Map<String, Object>>> grouped = new LinkedHashMap<>();
        grouped.put("overdue", new ArrayList<>());
        grouped.put("today", new ArrayList<>());
        grouped.put("soon", new ArrayList<>());
        grouped.put("backlog", new ArrayList<>());

        for (Map<String, Object> todo : openTodos) {
            String lane = asString(todo.get("focusLane"));
            grouped.computeIfAbsent(lane, ignored -> new ArrayList<>()).add(todo);
        }

        List<Map<String, Object>> lanes = new ArrayList<>();
        for (Map.Entry<String, List<Map<String, Object>>> entry : grouped.entrySet()) {
            List<Map<String, Object>> cards = entry.getValue().stream()
                .sorted(Comparator
                    .comparingInt((Map<String, Object> todo) -> asInteger(todo.get("focusScore"))).reversed()
                    .thenComparing(todo -> asString(todo.get("title"))))
                .map(todo -> {
                    Map<String, Object> card = new LinkedHashMap<>();
                    card.put("id", todo.get("id"));
                    card.put("title", todo.get("title"));
                    card.put("project", todo.get("project"));
                    card.put("priority", todo.get("priority"));
                    card.put("dueDate", todo.get("dueDate"));
                    card.put("estimateMinutes", todo.get("estimateMinutes"));
                    card.put("focusScore", todo.get("focusScore"));
                    card.put("focusLane", todo.get("focusLane"));
                    card.put("plannerReason", todo.get("plannerReason"));
                    return card;
                })
                .toList();
            Map<String, Object> lane = new LinkedHashMap<>();
            lane.put("lane", entry.getKey());
            lane.put("label", laneLabel(entry.getKey()));
            lane.put("accent", laneAccent(entry.getKey()));
            lane.put("todos", cards);
            lanes.add(lane);
        }
        return lanes;
    }

    private List<Map<String, Object>> buildProjectSnapshots(List<Map<String, Object>> todos) {
        Map<String, Map<String, Object>> snapshots = new LinkedHashMap<>();
        for (Map<String, Object> todo : todos) {
            String project = asString(todo.get("project"));
            Map<String, Object> snapshot = snapshots.computeIfAbsent(project, ignored -> {
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("project", project);
                item.put("openCount", 0);
                item.put("completedCount", 0);
                item.put("criticalCount", 0);
                return item;
            });
            if (asBoolean(todo.get("completed"))) {
                snapshot.put("completedCount", asInteger(snapshot.get("completedCount")) + 1);
            } else {
                snapshot.put("openCount", asInteger(snapshot.get("openCount")) + 1);
            }
            if ("critical".equalsIgnoreCase(asString(todo.get("priority")))) {
                snapshot.put("criticalCount", asInteger(snapshot.get("criticalCount")) + 1);
            }
        }
        return new ArrayList<>(snapshots.values());
    }

    private List<Map<String, Object>> fetchProjectedTodos() {
        Map<String, Object> selection = new LinkedHashMap<>();
        selection.put("->", Map.of("Ok_", List.of("todos")));
        selection.put(
            "struct.Todo",
            List.of(
                "id",
                "title",
                "project",
                "priority",
                "dueDate",
                "estimateMinutes",
                "focusScore",
                "focusLane",
                "plannerReason",
                "completed"
            )
        );
        Message response = this.todoClient.request(
            Map.of("@select_", selection),
            Map.of(
                "fn.listTodos",
                Map.of(
                    "status", "all",
                    "search", "",
                    "project", "",
                    "tag", ""
                )
            )
        );
        if (!"Ok_".equals(response.getBodyTarget())) {
            throw new RuntimeException("Todo service request failed: " + response.body);
        }
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> todos = (List<Map<String, Object>>) response.getBodyPayload().get("todos");
        return todos;
    }

    private String laneLabel(String lane) {
        return switch (lane) {
            case "overdue" -> "Overdue";
            case "today" -> "Today";
            case "soon" -> "Soon";
            default -> "Backlog";
        };
    }

    private String laneAccent(String lane) {
        return switch (lane) {
            case "overdue" -> "#9d2b25";
            case "today" -> "#d96f32";
            case "soon" -> "#2f6a7a";
            default -> "#53734d";
        };
    }

    private static String asString(Object value) {
        return String.valueOf(value);
    }

    private static String asNullableString(Object value) {
        return value == null ? null : String.valueOf(value);
    }

    private static int asInteger(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        return Integer.parseInt(String.valueOf(value));
    }

    private static boolean asBoolean(Object value) {
        if (value instanceof Boolean bool) {
            return bool;
        }
        return Boolean.parseBoolean(String.valueOf(value));
    }

    @SuppressWarnings("unchecked")
    private static List<String> asStringList(Object value) {
        if (value == null) {
            return List.of();
        }
        return ((List<Object>) value).stream().map(String::valueOf).toList();
    }
}
