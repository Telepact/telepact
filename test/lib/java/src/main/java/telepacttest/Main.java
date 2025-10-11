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

package telepacttest;

import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.util.Base64;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.BiFunction;
import java.util.function.Function;

import com.codahale.metrics.CsvReporter;
import com.codahale.metrics.MetricRegistry;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.module.SimpleModule;

import io.github.telepact.Client;
import io.github.telepact.TestClient;
import io.github.telepact.Message;
import io.github.telepact.MockServer;
import io.github.telepact.MockTelepactSchema;
import io.github.telepact.SerializationError;
import io.github.telepact.Serializer;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaParseError;
import telepacttest.gen.TypedClient;
import telepacttest.gen.test;
import io.github.telepact.TelepactSchemaFiles;
import io.nats.client.Dispatcher;
import io.nats.client.Nats;
import io.nats.client.Options;

public class Main {
    public static class CustomByteArraySerializer extends JsonSerializer<byte[]> {
        @Override
        public void serialize(byte[] value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
            System.out.println("Using custom serializer for byte array");
            String base64 = Base64.getEncoder().encodeToString(value);
            gen.writeString(base64);
        }
    }

    private static boolean containsBytesArray(Object data) {
        if (data instanceof byte[]) {
            return true;
        }

        if (data == null) {
            return false;
        }

        if (data instanceof Map<?, ?>) {
            Map<?, ?> map = (Map<?, ?>) data;
            for (Object value : map.values()) {
                if (containsBytesArray(value)) {
                    return true;
                }
            }
        }

        if (data instanceof Collection<?>) {
            Collection<?> collection = (Collection<?>) data;
            for (Object element : collection) {
                if (containsBytesArray(element)) {
                    return true;
                }
            }
        }

        return false;
    }    

    public static Dispatcher startClientTestServer(io.nats.client.Connection connection, MetricRegistry metrics,
            String clientFrontdoorTopic,
            String clientBackdoorTopic, boolean defaultBinary, boolean useCodeGen,
            boolean useTestClient)
            throws IOException, InterruptedException {
        var objectMapper = new ObjectMapper();

        SimpleModule module = new SimpleModule();
        module.addSerializer(byte[].class, new CustomByteArraySerializer());
        objectMapper.registerModule(module);

        var timers = metrics.timer(clientFrontdoorTopic);

        BiFunction<Message, Serializer, Future<Message>> adapter = (m, s) -> {
            return CompletableFuture.supplyAsync(() -> {
                try {
                    byte[] requestBytes;
                    try {
                        requestBytes = s.serialize(m);
                    } catch (SerializationError e) {
                        if (e.getCause() instanceof IllegalArgumentException) {
                            return new Message(Map.of("numberTooBig", true), Map.of("ErrorUnknown_", Map.of()));
                        } else {
                            throw e;
                        }
                    }

                    System.out.println("   <-c  %s".formatted(new String(requestBytes)));
                    System.out.flush();

                    io.nats.client.Message natsResponseMessage;
                    try {
                        natsResponseMessage = connection.request(clientBackdoorTopic, requestBytes,
                                Duration.ofSeconds(5));
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                    var responseBytes = natsResponseMessage.getData();

                    System.out.println("   ->c  %s".formatted(new String(responseBytes)));
                    System.out.flush();

                    var responseMessage = s.deserialize(responseBytes);
                    return responseMessage;
                } catch (Exception e) {
                    e.printStackTrace();
                    throw new RuntimeException(e);
                }
            });
        };

        var options = new Client.Options();
        options.useBinary = defaultBinary;
        options.alwaysSendJson = !defaultBinary;
        var client = new Client(adapter, options);

        var testClientOptions = new TestClient.Options();
        var testClient = new TestClient(client, testClientOptions);

        var generatedClient = new TypedClient(client);

        var dispatcher = connection.createDispatcher((msg) -> {
            try {
                var requestBytes = msg.getData();

                System.out.println("   ->C  %s".formatted(new String(requestBytes)));
                System.out.flush();

                var requestPseudoJson = objectMapper.readValue(requestBytes, List.class);
                var requestHeaders = (Map<String, Object>) requestPseudoJson.get(0);
                var requestBody = (Map<String, Object>) requestPseudoJson.get(1);
                var request = new Message(requestHeaders, requestBody);

                var entry = requestBody.entrySet().stream().findAny().get();
                var functionName = entry.getKey();

                Message response;

                if (useTestClient) {
                    try {
                        var resetSeed = (Integer) requestHeaders.get("@setSeed");
                        if (resetSeed != null) {
                            testClient.setSeed(resetSeed);
                        }
                        var expectedPseudoJsonBody = (Map<String, Object>) requestHeaders.get("@expectedPseudoJsonBody");
                        var expectMatch = (Boolean) requestHeaders.getOrDefault("@expectMatch", true);
                        response = testClient.assertRequest(request, expectedPseudoJsonBody, expectMatch);
                    } catch (Throwable e) {
                        e.printStackTrace();
                        var responseHeaders = new HashMap<String, Object>();
                        if (e instanceof AssertionError) {
                            responseHeaders.put("@assertionError", true);
                        }
                        response = new Message(responseHeaders, Map.of("ErrorUnknown_", Map.of()));
                    }
                } else {
                    if (useCodeGen && "fn.test".equals(functionName)) {
                        var outputMessage = generatedClient.test(requestHeaders, new test.Input(requestBody));
                        var responseHeaders = outputMessage.headers;
                        responseHeaders.put("@codegenc_", true);
                        response = new Message(responseHeaders, outputMessage.body.pseudoJson);
                    } else {

                        try (var time = timers.time()) {
                            response = client.request(request);
                        }
                    }
                }

                var responsePseudoJson = List.of(response.headers, response.body);

                System.out.println("   <-C  %s".formatted(responsePseudoJson));
                try {
                    var body = (Map<String, Object>) responsePseudoJson.get(1);
                    var ok = (Map<String, Object>) body.get("Ok_");
                    var value = (Map<String, Object>) ok.get("value!");
                    var bytes = value.get("bytes!");
                    System.out.println("bytes: %s".formatted(bytes));
                    System.out.println("bytes class: " + bytes.getClass());
                } catch (Exception e) {
                    // ignore
                }

                var clientReturnedBinary = containsBytesArray(responsePseudoJson);

                if (clientReturnedBinary) {
                    ((Map<String, Object>)responsePseudoJson.get(0)).put("@clientReturnedBinary", true);
                }

                var responseBytes = objectMapper.writeValueAsBytes(responsePseudoJson);

                System.out.println("   <-C  %s".formatted(new String(responseBytes)));
                System.out.flush();

                connection.publish(msg.getReplyTo(), responseBytes);
            } catch (Exception e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
        });
        dispatcher.subscribe(clientFrontdoorTopic);

        return dispatcher;
    }

    public static Dispatcher startMockTestServer(io.nats.client.Connection connection, MetricRegistry metrics,
            String apiSchemaPath,
            String frontdoorTopic,
            Map<String, Object> config)
            throws IOException, InterruptedException {
        var telepact = MockTelepactSchema.fromDirectory(apiSchemaPath);

        var options = new MockServer.Options();
        options.onError = (e) -> e.printStackTrace();
        options.enableMessageResponseGeneration = false;

        if (config != null) {
            options.generatedCollectionLengthMin = (Integer) config.get("minLength");
            options.generatedCollectionLengthMax = (Integer) config.get("maxLength");
            options.enableMessageResponseGeneration = (Boolean) config.get("enableGen");
        }

        var timers = metrics.timer(frontdoorTopic);

        var server = new MockServer(telepact, options);

        var dispatcher = connection.createDispatcher((msg) -> {
            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();

            byte[] responseBytes;
            try (var time = timers.time()) {
                final var response = server.process(requestBytes);
                responseBytes = response.bytes;
            }

            System.out.println("    <-S %s".formatted(new String(responseBytes)));
            System.out.flush();

            connection.publish(msg.getReplyTo(), responseBytes);
        });
        dispatcher.subscribe(frontdoorTopic);

        return dispatcher;
    }

    public static Dispatcher startSchemaTestServer(io.nats.client.Connection connection, MetricRegistry metrics,
            String apiSchemaPath,
            String frontdoorTopic)
            throws IOException, InterruptedException {
        var telepact = TelepactSchema.fromDirectory(apiSchemaPath);
        var objectMapper = new ObjectMapper();

        var timers = metrics.timer(frontdoorTopic);

        Function<Message, Message> handler = (requestMessage) -> {
            var requestBody = requestMessage.body;

            var arg = (Map<String, Object>) requestBody.get("fn.validateSchema");
            var input = (Map<String, Object>) arg.get("input");

            var inputTag = input.keySet().iterator().next();

            try {
                if (inputTag.equals("PseudoJson")) {
                    var unionValue = (Map<String, Object>) input.get(inputTag);
                    var schemaJson = (String) unionValue.get("schema");
                    var extendJson = (String) unionValue.get("extend!");

                    if (extendJson != null) {
                        TelepactSchema.fromFileJsonMap(Map.of("default", schemaJson, "extend", extendJson));
                    } else {
                        TelepactSchema.fromJson(schemaJson);
                    }
                } else if (inputTag.equals("Json")) {
                    var unionValue = (Map<String, Object>) input.get(inputTag);
                    var schemaJson = (String) unionValue.get("schema");
                    TelepactSchema.fromJson(schemaJson);
                } else if (inputTag.equals("Directory")) {
                    var unionValue = (Map<String, Object>) input.get(inputTag);
                    var schemaPath = (String) unionValue.get("schemaDirectory");
                    TelepactSchema.fromDirectory(schemaPath);
                } else {
                    throw new RuntimeException("unknown input tag");
                }
            } catch (TelepactSchemaParseError e) {
                e.printStackTrace();
                System.err.flush();
                return new Message(Map.of(),
                        Map.of("ErrorValidationFailure", Map.of("cases", e.schemaParseFailuresPseudoJson)));
            }

            return new Message(Map.of(), Map.of("Ok_", Map.of()));
        };

        var options = new Server.Options();
        options.onError = (e) -> {
            e.printStackTrace();
            System.err.flush();
        };
        options.authRequired = false;
        var server = new Server(telepact, handler, options);

        var dispatcher = connection.createDispatcher((msg) -> {
            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();

            byte[] responseBytes;
            try (var time = timers.time()) {
                var response = server.process(requestBytes);
                responseBytes = response.bytes;
            }

            System.out.println("    <-S %s".formatted(new String(responseBytes)));
            System.out.flush();

            connection.publish(msg.getReplyTo(), responseBytes);
        });
        dispatcher.subscribe(frontdoorTopic);

        return dispatcher;
    }

    public static Dispatcher startTestServer(io.nats.client.Connection connection, MetricRegistry metrics,
            String apiSchemaPath,
            String frontdoorTopic,
            String backdoorTopic, boolean authRequired, boolean useCodeGen)
            throws IOException, InterruptedException {
        var files = new TelepactSchemaFiles(apiSchemaPath);
        var alternateMap = new HashMap<>(files.filenamesToJson);
        alternateMap.put("backwardsCompatibleChange", """
                [
                    {
                        "struct.BackwardsCompatibleChange": {}
                    }
                ]
                """);

        var telepact = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
        var alternateTelepact = TelepactSchema.fromFileJsonMap(alternateMap);

        var objectMapper = new ObjectMapper();

        SimpleModule module = new SimpleModule();
        module.addSerializer(byte[].class, new CustomByteArraySerializer());
        objectMapper.registerModule(module);

        var timers = metrics.timer(frontdoorTopic);

        var serveAlternateServer = new AtomicBoolean();

        CodeGenHandler codeGenHandler = new CodeGenHandler();

        class ThisError extends RuntimeException {
        }

        Function<Message, Message> handler = (requestMessage) -> {
            try {
                var requestHeaders = requestMessage.headers;
                var requestBody = requestMessage.body;
                var requestPseudoJson = List.of(requestHeaders, requestBody);

                var requestBytes = objectMapper.writeValueAsBytes(requestPseudoJson);

                Message message;
                if (useCodeGen) {
                    System.out.println("     :H %s".formatted(objectMapper.writeValueAsString(requestPseudoJson)));
                    message = codeGenHandler.handler(requestMessage);
                    message.headers.put("@codegens_", true);
                } else {
                    System.out.println("    <-s %s".formatted(new String(requestBytes)));
                    System.out.flush();

                    io.nats.client.Message natsResponseMessage;
                    try {
                        natsResponseMessage = connection.request(backdoorTopic, requestBytes, Duration.ofSeconds(5));
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                    var responseBytes = natsResponseMessage.getData();

                    System.out.println("    ->s %s".formatted(new String(responseBytes)));
                    System.out.flush();

                    var responsePseudoJson = objectMapper.readValue(responseBytes, List.class);
                    var responseHeaders = (Map<String, Object>) responsePseudoJson.get(0);
                    var responseBody = (Map<String, Object>) responsePseudoJson.get(1);

                    message = new Message(responseHeaders, responseBody);

                }

                var toggleAlternateServer = requestHeaders.get("@toggleAlternateServer_");
                if (Objects.equals(true, toggleAlternateServer)) {
                    serveAlternateServer.set(!serveAlternateServer.get());
                }

                var throwError = requestHeaders.get("@throwError_");
                if (Objects.equals(true, throwError)) {
                    throw new ThisError();
                }

                return message;
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };

        var options = new Server.Options();
        options.onError = (e) -> {
            e.printStackTrace();
            System.err.flush();
            if (e.getCause() instanceof ThisError) {
                throw new RuntimeException();
            }
        };
        options.onRequest = m -> {
            if ((Boolean) m.headers.getOrDefault("@onRequestError_", false)) {
                throw new RuntimeException();
            }
        };
        options.onResponse = m -> {
            if ((Boolean) m.headers.getOrDefault("@onResponseError_", false)) {
                throw new RuntimeException();
            }
        };
        options.authRequired = authRequired;

        var server = new Server(telepact, handler, options);

        var alternateOptions = new Server.Options();
        alternateOptions.onError = (e) -> e.printStackTrace();
        alternateOptions.authRequired = authRequired;

        var alternateServer = new Server(alternateTelepact, handler, alternateOptions);

        var dispatcher = connection.createDispatcher((msg) -> {

            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();

            byte[] responseBytes;
            try (var time = timers.time()) {
                if (serveAlternateServer.get()) {
                    final var response = alternateServer.process(requestBytes);
                    responseBytes = response.bytes;
                } else {
                    Map<String, Object> overrideHeaders = Map.of("@override", "new");
                    final var response = server.process(requestBytes, overrideHeaders);
                    responseBytes = response.bytes;
                }
            }
            System.out.println("    <-S %s".formatted(new String(responseBytes)));
            System.out.flush();

            connection.publish(msg.getReplyTo(), responseBytes);
        });

        dispatcher.subscribe(frontdoorTopic);

        System.out.println("Test server listening on " + frontdoorTopic);

        return dispatcher;
    }

    private static void runDispatcherServer() throws InterruptedException, IOException {
        var natsUrl = System.getenv("NATS_URL");
        if (natsUrl == null) {
            throw new RuntimeException("NATS_URL env var not set");
        }

        var natsOptionsBuilder = new Options.Builder();
        natsOptionsBuilder.server(natsUrl);

        var objectMapper = new ObjectMapper();

        var lock = new ReentrantLock();
        var done = lock.newCondition();

        final var metrics = new MetricRegistry();
        var metricsFile = new File("./metrics/");
        var metricsReporter = CsvReporter.forRegistry(metrics).build(metricsFile);

        var servers = new HashMap<String, Dispatcher>();
        try (var connection = Nats.connect(natsOptionsBuilder.build())) {
            var dispatcher = connection.createDispatcher((msg) -> {
                var requestBytes = msg.getData();

                System.out.println("    ->S %s".formatted(new String(requestBytes)));
                System.out.flush();

                byte[] responseBytes;
                try {
                    var request = (List<Object>) objectMapper.readValue(requestBytes, List.class);
                    var body = (Map<String, Object>) request.get(1);
                    var entry = body.entrySet().stream().findAny().get();
                    var target = entry.getKey();
                    var payload = (Map<String, Object>) entry.getValue();

                    switch (target) {
                        case "Ping" -> {

                        }
                        case "End" -> {
                            lock.lock();
                            done.signalAll();
                            lock.unlock();
                        }
                        case "Stop" -> {
                            var id = (String) payload.get("id");
                            var d = servers.get(id);
                            if (d != null) {
                                d.drain(Duration.ofSeconds(1)).get();
                            }
                        }
                        case "StartServer" -> {
                            var id = (String) payload.get("id");
                            var apiSchemaPath = (String) payload.get("apiSchemaPath");
                            var frontdoorTopic = (String) payload.get("frontdoorTopic");
                            var backdoorTopic = (String) payload.get("backdoorTopic");
                            var authRequired = (Boolean) payload.getOrDefault("authRequired!", false);
                            var useCodeGen = (Boolean) payload.getOrDefault("useCodeGen", false);

                            var d = startTestServer(connection, metrics, apiSchemaPath, frontdoorTopic,
                                    backdoorTopic, authRequired, useCodeGen);

                            servers.put(id, d);
                        }
                        case "StartClientServer" -> {
                            var id = (String) payload.get("id");
                            var clientFrontdoorTopic = (String) payload.get("clientFrontdoorTopic");
                            var clientBackdoorTopic = (String) payload.get("clientBackdoorTopic");
                            var useBinary = (Boolean) payload.getOrDefault("useBinary", false);
                            var useCodeGen = (Boolean) payload.getOrDefault("useCodeGen", false);
                            var useTestClient = (Boolean) payload.getOrDefault("useTestClient", false);

                            var d = startClientTestServer(connection, metrics, clientFrontdoorTopic,
                                    clientBackdoorTopic,
                                    useBinary, useCodeGen, useTestClient);

                            servers.put(id, d);
                        }
                        case "StartMockServer" -> {
                            var id = (String) payload.get("id");
                            var apiSchemaPath = (String) payload.get("apiSchemaPath");
                            var frontdoorTopic = (String) payload.get("frontdoorTopic");
                            var config = (Map<String, Object>) payload.get("config!");
                            var d = startMockTestServer(connection, metrics, apiSchemaPath,
                                    frontdoorTopic, config);

                            servers.put(id, d);
                        }
                        case "StartSchemaServer" -> {
                            var id = (String) payload.get("id");
                            var apiSchemaPath = (String) payload.get("apiSchemaPath");
                            var frontdoorTopic = (String) payload.get("frontdoorTopic");
                            var d = startSchemaTestServer(connection, metrics, apiSchemaPath,
                                    frontdoorTopic);

                            servers.put(id, d);
                        }
                        default -> throw new RuntimeException("no matching server");
                    }
                    ;

                    responseBytes = objectMapper.writeValueAsBytes(List.of(Map.of(), Map.of("Ok_", Map.of())));
                } catch (Throwable e) {
                    e.printStackTrace();
                    try {
                        responseBytes = objectMapper
                                .writeValueAsBytes(List.of(Map.of(), Map.of("ErrorUnknown", Map.of())));
                    } catch (JsonProcessingException e1) {
                        throw new RuntimeException();
                    }
                }

                System.out.println("    <-S %s".formatted(new String(responseBytes)));
                System.out.flush();

                connection.publish(msg.getReplyTo(), responseBytes);
            });

            dispatcher.subscribe("java");

            lock.lock();
            done.await();

            //metricsReporter.report();

            System.out.println("Dispatcher exiting");
        }
    }

    public static void main(String[] args) throws InterruptedException, IOException {
        runDispatcherServer();
    }
}
