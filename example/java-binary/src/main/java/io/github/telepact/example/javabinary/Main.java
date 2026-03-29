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
import io.github.telepact.Client;
import io.github.telepact.Message;
import io.github.telepact.Serializer;
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
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Future;

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

    private static Server buildTelepactServer() {
        var files = new TelepactSchemaFiles("api");
        var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
        var options = new Server.Options();
        options.authRequired = false;
        return new Server(schema, requestMessage -> {
            var functionName = requestMessage.getBodyTarget();
            if (!"fn.numbers".equals(functionName)) {
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
        System.out.println("java-binary listening on http://127.0.0.1:" + port);
        new CountDownLatch(1).await();
    }

    private static void runCheck(String url) throws Exception {
        var requestContentTypes = new ArrayList<String>();
        var responseContentTypes = new ArrayList<String>();
        HttpClient httpClient = HttpClient.newHttpClient();

        var adapter = (java.util.function.BiFunction<Message, Serializer, Future<Message>>) (message, serializer) ->
                CompletableFuture.supplyAsync(() -> {
                    try {
                        var requestBytes = serializer.serialize(message);
                        var requestContentType = looksLikeJson(requestBytes)
                                ? "application/json"
                                : "application/octet-stream";
                        requestContentTypes.add(requestContentType);

                        var request = HttpRequest.newBuilder(URI.create(url))
                                .header("Content-Type", requestContentType)
                                .POST(HttpRequest.BodyPublishers.ofByteArray(requestBytes))
                                .build();
                        var response = httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray());
                        var responseContentType = response.headers()
                                .firstValue("content-type")
                                .orElse("missing");
                        responseContentTypes.add(responseContentType);
                        return serializer.deserialize(response.body());
                    } catch (Exception exception) {
                        throw new RuntimeException(exception);
                    }
                });

        var clientOptions = new Client.Options();
        clientOptions.useBinary = true;
        clientOptions.alwaysSendJson = false;
        var client = new Client(adapter, clientOptions);

        for (int i = 0; i < 2; i += 1) {
            var response = client.request(new Message(Map.of(), Map.of("fn.numbers", Map.of("limit", 3))));
            @SuppressWarnings("unchecked")
            var payload = (Map<String, Object>) response.body.get("Ok_");
            @SuppressWarnings("unchecked")
            var values = (List<Integer>) payload.get("values");
            if (!values.equals(List.of(1, 2, 3))) {
                throw new IllegalStateException("Unexpected response payload: " + response.body);
            }
        }

        if (requestContentTypes.size() < 2 || !"application/octet-stream".equals(requestContentTypes.get(1))) {
            throw new IllegalStateException("Expected second request to be binary, got " + requestContentTypes);
        }
        if (responseContentTypes.stream().noneMatch(value -> value.startsWith("application/octet-stream"))) {
            throw new IllegalStateException("Expected at least one binary response, got " + responseContentTypes);
        }

        System.out.println("java-binary check passed");
    }

    private static boolean looksLikeJson(byte[] bytes) {
        for (byte value : bytes) {
            if (!Character.isWhitespace(value)) {
                return value == '[' || value == '{';
            }
        }
        return false;
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
