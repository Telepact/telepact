package com.example.planner;

import com.sun.net.httpserver.HttpServer;
import io.github.telepact.Message;
import java.io.IOException;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

final class AppTest {
    private static int nextPort = 19300;
    private Process mockProcess;
    private HttpServer appServer;

    @AfterEach
    void cleanup() {
        if (this.appServer != null) {
            this.appServer.stop(0);
        }
        if (this.mockProcess != null) {
            this.mockProcess.destroy();
        }
    }

    @Test
    void dashboardUsesTodoMockAndReturnsProjectedData() throws Exception {
        int todoMockPort = reservePort();
        int appPort = reservePort();
        String root = Path.of("..", "..").toAbsolutePath().normalize().toString();
        this.mockProcess = new ProcessBuilder(
            Path.of(root, ".venv", "bin", "telepact").toString(),
            "mock",
            "--dir",
            Path.of(root, "schemas", "todo").toString(),
            "--port",
            String.valueOf(todoMockPort)
        )
            .directory(Path.of(root).toFile())
            .inheritIO()
            .start();
        waitForPort(todoMockPort);

        TelepactHttpClient mockClient = new TelepactHttpClient("http://127.0.0.1:" + todoMockPort + "/api");
        mockClient.request(Map.of("fn.createStub_", createListTodosStub()));

        this.appServer = App.startServer(
            new App.Config(
                appPort,
                Path.of(root, "schemas", "planner").toString(),
                "http://127.0.0.1:" + todoMockPort + "/api"
            )
        );
        waitForPort(appPort);

        TelepactHttpClient appClient = new TelepactHttpClient("http://127.0.0.1:" + appPort + "/api");
        Message response = appClient.request(Map.of("fn.getPlannerDashboard", Map.of()));

        Assertions.assertEquals("Ok_", response.getBodyTarget());
        @SuppressWarnings("unchecked")
        Map<String, Object> dashboard = (Map<String, Object>) response.getBodyPayload().get("dashboard");
        @SuppressWarnings("unchecked")
        Map<String, Object> summary = (Map<String, Object>) dashboard.get("summary");
        Assertions.assertEquals(1, ((Number) summary.get("openCount")).intValue());

        Message verification = mockClient.request(
            Map.of(
                "fn.verify_",
                Map.of(
                    "call",
                    Map.of(
                        "fn.listTodos",
                        Map.of(
                            "status", "all",
                            "search", "",
                            "project", "",
                            "tag", ""
                        )
                    )
                )
            )
        );
        Assertions.assertEquals("Ok_", verification.getBodyTarget());
    }

    @Test
    void startFocusSessionReturnsDomainErrorWhenTodoMissing() throws Exception {
        int todoMockPort = reservePort();
        int appPort = reservePort();
        String root = Path.of("..", "..").toAbsolutePath().normalize().toString();
        this.mockProcess = new ProcessBuilder(
            Path.of(root, ".venv", "bin", "telepact").toString(),
            "mock",
            "--dir",
            Path.of(root, "schemas", "todo").toString(),
            "--port",
            String.valueOf(todoMockPort)
        )
            .directory(Path.of(root).toFile())
            .inheritIO()
            .start();
        waitForPort(todoMockPort);

        TelepactHttpClient mockClient = new TelepactHttpClient("http://127.0.0.1:" + todoMockPort + "/api");
        mockClient.request(Map.of("fn.createStub_", createEmptyListTodosStub()));

        this.appServer = App.startServer(
            new App.Config(
                appPort,
                Path.of(root, "schemas", "planner").toString(),
                "http://127.0.0.1:" + todoMockPort + "/api"
            )
        );
        waitForPort(appPort);

        TelepactHttpClient appClient = new TelepactHttpClient("http://127.0.0.1:" + appPort + "/api");
        Message response = appClient.request(
            Map.of("fn.startFocusSession", Map.of("todoId", "missing", "minutes", 25))
        );

        Assertions.assertEquals("ErrorTodoNotFound", response.getBodyTarget());
    }

    private static Map<String, Object> createListTodosStub() {
        Map<String, Object> firstTodo = new LinkedHashMap<>();
        firstTodo.put("id", "todo-1");
        firstTodo.put("title", "Audit onboarding");
        firstTodo.put("project", "Launch");
        firstTodo.put("priority", "critical");
        firstTodo.put("dueDate", "2030-01-18");
        firstTodo.put("estimateMinutes", 35);
        firstTodo.put("focusScore", 95);
        firstTodo.put("focusLane", "today");
        firstTodo.put("plannerReason", "Due today.");
        firstTodo.put("completed", false);

        Map<String, Object> secondTodo = new LinkedHashMap<>();
        secondTodo.put("id", "todo-2");
        secondTodo.put("title", "Archive changelog");
        secondTodo.put("project", "Launch");
        secondTodo.put("priority", "medium");
        secondTodo.put("dueDate", null);
        secondTodo.put("estimateMinutes", 10);
        secondTodo.put("focusScore", 45);
        secondTodo.put("focusLane", "backlog");
        secondTodo.put("plannerReason", "No deadline.");
        secondTodo.put("completed", true);

        return Map.of(
            "stub",
            Map.of(
                "fn.listTodos",
                Map.of(
                    "status", "all",
                    "search", "",
                    "project", "",
                    "tag", ""
                ),
                "->",
                Map.of(
                    "Ok_",
                    Map.of(
                        "todos",
                        List.of(firstTodo, secondTodo)
                    )
                )
            )
        );
    }

    private static Map<String, Object> createEmptyListTodosStub() {
        return Map.of(
            "stub",
            Map.of(
                "fn.listTodos",
                Map.of(
                    "status", "all",
                    "search", "",
                    "project", "",
                    "tag", ""
                ),
                "->",
                Map.of("Ok_", Map.of("todos", List.of()))
            )
        );
    }

    private static int reservePort() throws IOException {
        return nextPort++;
    }

    private static void waitForPort(int port) throws Exception {
        long deadline = System.currentTimeMillis() + 10_000;
        while (System.currentTimeMillis() < deadline) {
            try (java.net.Socket ignored = new java.net.Socket("127.0.0.1", port)) {
                return;
            } catch (IOException ignored) {
                Thread.sleep(100);
            }
        }
        throw new IllegalStateException("Timed out waiting for port " + port);
    }
}
