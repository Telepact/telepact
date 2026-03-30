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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sun.net.httpserver.HttpServer;
import io.github.telepact.Client;
import io.github.telepact.Message;
import io.github.telepact.Serializer;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;

final class MainTest {
    @Test
    void negotiatesBinaryAfterTheInitialRequest() throws Exception {
        HttpServer server = Main.startHttpServer(0);
        try {
            var url = "http://127.0.0.1:" + server.getAddress().getPort() + "/api/telepact";
            var requestContentTypes = Collections.synchronizedList(new ArrayList<String>());
            var responseContentTypes = Collections.synchronizedList(new ArrayList<String>());
            HttpClient httpClient = HttpClient.newHttpClient();

            var adapter = (java.util.function.BiFunction<Message, Serializer, Future<Message>>) (message, serializer) ->
                    CompletableFuture.supplyAsync(() -> {
                        try {
                            var requestBytes = serializer.serialize(message);
                            var requestContentType = Main.looksLikeJson(requestBytes)
                                    ? "application/json"
                                    : "application/octet-stream";
                            requestContentTypes.add(requestContentType);

                            var request = HttpRequest.newBuilder(URI.create(url))
                                    .header("Content-Type", requestContentType)
                                    .POST(HttpRequest.BodyPublishers.ofByteArray(requestBytes))
                                    .build();
                            var response = httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray());
                            responseContentTypes.add(response.headers().firstValue("content-type").orElse("missing"));
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
                assertEquals(List.of(1, 2, 3), values);
            }

            assertTrue(requestContentTypes.size() >= 2, requestContentTypes.toString());
            assertEquals("application/octet-stream", requestContentTypes.get(1));
            assertTrue(
                    responseContentTypes.stream().anyMatch(value -> value.startsWith("application/octet-stream")),
                    responseContentTypes.toString());
        } finally {
            server.stop(0);
        }
    }
}
