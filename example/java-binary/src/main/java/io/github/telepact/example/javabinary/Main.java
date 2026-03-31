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

package io.github.telepact.example.javabinary;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import io.github.telepact.Message;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaFiles;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Map;

public final class Main {
    private Main() {}

    static Server buildTelepactServer() {
        var files = new TelepactSchemaFiles("api");
        var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
        var options = new Server.Options();
        options.authRequired = false;
        return new Server(schema, requestMessage -> {
            var functionName = requestMessage.getBodyTarget();
            if (!"fn.getNumbers".equals(functionName)) {
                throw new IllegalArgumentException("Unknown function: " + functionName);
            }
            var arguments = requestMessage.getBodyPayload();
            var limit = ((Number) arguments.get("limit")).intValue();
            var values = new ArrayList<Integer>();
            for (int i = 1; i <= limit; i += 1) {
                values.add(i);
            }
            return new Message(Map.of(), Map.of("Ok_", Map.of("values", values)));
        }, options);
    }

    static HttpServer startHttpServer(int port) throws IOException {
        var server = buildTelepactServer();
        var httpServer = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        httpServer.createContext("/api/telepact", exchange -> handleTelepact(exchange, server));
        httpServer.start();
        return httpServer;
    }

    static boolean looksLikeJson(byte[] bytes) {
        for (byte value : bytes) {
            if (!Character.isWhitespace(value)) {
                return value == '[' || value == '{';
            }
        }
        return false;
    }

    private static void handleTelepact(HttpExchange exchange, Server server) throws IOException {
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
