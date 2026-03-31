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
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.concurrent.LinkedBlockingQueue;
import org.junit.jupiter.api.Test;

final class MainTest {
    record EncodedRequest(byte[] bytes, String encoding) {}

    @Test
    void negotiatesBinaryAfterTheInitialRequest() throws Exception {
        var server = Main.buildTelepactServer();
        var requestEncodings = Collections.synchronizedList(new ArrayList<String>());
        var responseEncodings = Collections.synchronizedList(new ArrayList<String>());
        BlockingQueue<EncodedRequest> requests = new LinkedBlockingQueue<>();
        BlockingQueue<byte[]> responses = new LinkedBlockingQueue<>();

        var serverLoop = CompletableFuture.runAsync(() -> {
            try {
                while (true) {
                    var request = requests.take();
                    if (request.bytes.length == 0) {
                        return;
                    }

                    requestEncodings.add(request.encoding);
                    var response = server.process(request.bytes);
                    responseEncodings.add(response.headers.containsKey("@bin_") ? "binary" : "json");
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
                        var requestEncoding = Main.looksLikeJson(requestBytes) ? "json" : "binary";
                        requests.put(new EncodedRequest(requestBytes, requestEncoding));
                        return serializer.deserialize(responses.take());
                    } catch (InterruptedException exception) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException(exception);
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

        assertTrue(requestEncodings.size() >= 2, requestEncodings.toString());
        assertEquals("binary", requestEncodings.get(1));
        assertTrue(responseEncodings.contains("binary"), responseEncodings.toString());

        requests.put(new EncodedRequest(new byte[0], "shutdown"));
        serverLoop.get();
    }
}
