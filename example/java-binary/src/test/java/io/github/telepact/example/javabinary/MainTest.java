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

import io.github.telepact.Client;
import io.github.telepact.Message;
import io.github.telepact.Serializer;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

final class MainTest {
    private static byte[] putRequestAndTakeResponse(BlockingQueue<byte[]> requests, BlockingQueue<byte[]> responses,
            byte[] requestBytes) {
        try {
            requests.put(requestBytes);
            return responses.take();
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            throw new RuntimeException(exception);
        }
    }

    private static boolean looksLikeJson(byte[] bytes) {
        for (byte value : bytes) {
            if (!Character.isWhitespace(value)) {
                return value == '[' || value == '{';
            }
        }
        return false;
    }

    @Test
    void negotiatesBinaryAfterTheInitialRequest() throws Exception {
        var server = Main.buildTelepactServer();
        BlockingQueue<byte[]> requests = new LinkedBlockingQueue<>();
        BlockingQueue<byte[]> responses = new LinkedBlockingQueue<>();
        AtomicInteger requestCount = new AtomicInteger();
        AtomicBoolean sawBinaryResponse = new AtomicBoolean(false);

        var serverLoop = CompletableFuture.runAsync(() -> {
            try {
                while (true) {
                    var request = requests.take();
                    if (request.length == 0) {
                        return;
                    }

                    var requestIndex = requestCount.getAndIncrement();
                    if (requestIndex == 0) {
                        assertTrue(looksLikeJson(request), "first request should be json");
                    } else if (requestIndex == 1) {
                        assertTrue(!looksLikeJson(request), "second request should be binary");
                    }
                    var response = server.process(request);
                    if (response.headers.containsKey("@bin_")) {
                        sawBinaryResponse.set(true);
                    }
                    responses.put(response.bytes);
                }
            } catch (InterruptedException exception) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(exception);
            }
        });

        var adapter = (java.util.function.BiFunction<Message, Serializer, Future<Message>>) (message, serializer) ->
                CompletableFuture.supplyAsync(() -> {
                    try {
                        var requestBytes = serializer.serialize(message);
                        var responseBytes = putRequestAndTakeResponse(requests, responses, requestBytes);
                        return serializer.deserialize(responseBytes);
                    } catch (Exception exception) {
                        throw new RuntimeException(exception);
                    }
                });

        var clientOptions = new Client.Options();
        clientOptions.useBinary = true;
        clientOptions.alwaysSendJson = false;
        var client = new Client(adapter, clientOptions);

        for (int i = 0; i < 2; i += 1) {
            var response = client.request(new Message(Map.of(), Map.of("fn.getNumbers", Map.of("limit", 3))));
            @SuppressWarnings("unchecked")
            var payload = (Map<String, Object>) response.body.get("Ok_");
            @SuppressWarnings("unchecked")
            var values = (List<Integer>) payload.get("values");
            assertEquals(List.of(1, 2, 3), values);
        }

        assertTrue(requestCount.get() >= 2, Integer.toString(requestCount.get()));
        assertTrue(sawBinaryResponse.get(), "expected at least one binary response");

        requests.put(new byte[0]);
        serverLoop.get();
    }
}
