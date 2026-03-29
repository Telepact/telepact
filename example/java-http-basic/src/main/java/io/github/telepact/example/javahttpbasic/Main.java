//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.example.javahttpbasic;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import io.github.telepact.Message;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaFiles;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

public final class Main {
    private Main() {}

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            throw new IllegalArgumentException("Usage: server <port> | check <url>");
        }

        if ("server".equals(args[0])) {
            runServer(Integer.parseInt(args[1]));
            return;
        }

        if ("check".equals(args[0])) {
            runCheck(args[1]);
            return;
        }

        throw new IllegalArgumentException("Unknown mode: " + args[0]);
    }

    private static void runServer(int port) throws Exception {
        var server = buildTelepactServer();
        var httpServer = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        httpServer.createContext("/healthz", exchange -> respondText(exchange, 200, "ok"));
        httpServer.createContext("/api/telepact", exchange -> {
            if (!"POST".equals(exchange.getRequestMethod())) {
                exchange.sendResponseHeaders(405, -1);
                exchange.close();
                return;
            }
            var requestBytes = exchange.getRequestBody().readAllBytes();
            var response = server.process(requestBytes);
            var contentType = response.headers.containsKey("@bin_")
                    ? "application/octet-stream"
                    : "application/json";
            exchange.getResponseHeaders().set("Content-Type", contentType);
            exchange.sendResponseHeaders(200, response.bytes.length);
            try (OutputStream outputStream = exchange.getResponseBody()) {
                outputStream.write(response.bytes);
            }
        });
        httpServer.start();
        System.out.println("java-http-basic listening on http://127.0.0.1:" + port);
        new CountDownLatch(1).await();
    }

    private static Server buildTelepactServer() {
        var files = new TelepactSchemaFiles("api");
        var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
        var options = new Server.Options();
        options.authRequired = false;
        return new Server(schema, requestMessage -> {
            var functionName = requestMessage.getBodyTarget();
            var arguments = requestMessage.getBodyPayload();
            if ("fn.hello".equals(functionName)) {
                var name = (String) arguments.get("name");
                return new Message(Map.of(), Map.of("Ok_", Map.of("message", "Hello " + name + "!")));
            }
            throw new IllegalArgumentException("Unknown function: " + functionName);
        }, options);
    }

    private static void runCheck(String url) throws Exception {
        var client = HttpClient.newHttpClient();
        var request = HttpRequest.newBuilder(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString("[{}, {\"fn.hello\": {\"name\": \"Telepact\"}}]"))
                .build();
        var response = client.send(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        if (response.statusCode() != 200) {
            throw new IllegalStateException("Expected 200, got " + response.statusCode());
        }
        if (!response.body().contains("Hello Telepact!")) {
            throw new IllegalStateException("Unexpected response body: " + response.body());
        }
        System.out.println("java-http-basic check passed");
    }

    private static void respondText(HttpExchange exchange, int status, String body) throws IOException {
        var bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream outputStream = exchange.getResponseBody()) {
            outputStream.write(bytes);
        }
    }
}
