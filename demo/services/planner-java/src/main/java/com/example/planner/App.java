package com.example.planner;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import io.github.telepact.Response;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.Executors;

public final class App {
    public static final class Config {
        public final int port;
        public final String schemaDir;
        public final String todoServiceUrl;

        public Config(int port, String schemaDir, String todoServiceUrl) {
            this.port = port;
            this.schemaDir = schemaDir;
            this.todoServiceUrl = todoServiceUrl;
        }

        public static Config fromEnvironment() {
            int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "7002"));
            String schemaDir = System.getenv().getOrDefault(
                "SCHEMA_DIR",
                Path.of("..", "..", "schemas", "planner").normalize().toString()
            );
            String todoServiceUrl = System.getenv().getOrDefault(
                "TODO_SERVICE_URL",
                "http://127.0.0.1:7001/api"
            );
            return new Config(port, schemaDir, todoServiceUrl);
        }
    }

    private App() {
    }

    public static void main(String[] args) throws Exception {
        HttpServer server = startServer(Config.fromEnvironment());
        Runtime.getRuntime().addShutdownHook(new Thread(() -> server.stop(0)));
    }

    public static HttpServer startServer(Config config) throws IOException {
        TelepactSchema schema = TelepactSchema.fromDirectory(config.schemaDir);
        PlannerService plannerService = new PlannerService(config.todoServiceUrl);
        Server.Options options = new Server.Options();
        options.authRequired = false;
        Server telepactServer = new Server(schema, plannerService::handle, options);

        HttpServer server = HttpServer.create(new InetSocketAddress(config.port), 0);
        server.createContext("/health", exchange -> writeJson(exchange, 200, "{\"status\":\"ok\"}"));
        server.createContext("/api", exchange -> {
            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                writeJson(exchange, 405, "{\"error\":\"Method Not Allowed\"}");
                return;
            }
            byte[] requestBytes = exchange.getRequestBody().readAllBytes();
            Response response = telepactServer.process(requestBytes);
            exchange.getResponseHeaders().set("content-type", "application/json");
            for (Map.Entry<String, Object> entry : response.headers.entrySet()) {
                exchange.getResponseHeaders().set(entry.getKey(), String.valueOf(entry.getValue()));
            }
            exchange.sendResponseHeaders(200, response.bytes.length);
            try (OutputStream outputStream = exchange.getResponseBody()) {
                outputStream.write(response.bytes);
            }
        });
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
        return server;
    }

    private static void writeJson(HttpExchange exchange, int statusCode, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("content-type", "application/json");
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream outputStream = exchange.getResponseBody()) {
            outputStream.write(bytes);
        }
    }
}
