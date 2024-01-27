package io.github.brenbar.uapi;

import java.io.File;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.time.Duration;
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

import org.junit.jupiter.api.Test;

import com.codahale.metrics.CsvReporter;
import com.codahale.metrics.MetricRegistry;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.nats.client.Connection;
import io.nats.client.Dispatcher;
import io.nats.client.Nats;
import io.nats.client.Options;

public class TestDispatch {

    public static Dispatcher startClientTestServer(Connection connection, MetricRegistry metrics,
            String clientFrontdoorTopic,
            String clientBackdoorTopic, boolean defaultBinary)
            throws IOException, InterruptedException {
        var objectMapper = new ObjectMapper();

        var timers = metrics.timer(clientFrontdoorTopic);

        BiFunction<Message, Serializer, Future<Message>> adapter = (m, s) -> {
            return CompletableFuture.supplyAsync(() -> {
                try {
                    byte[] requestBytes;
                    try {
                        requestBytes = s.serialize(m);
                    } catch (SerializationError e) {
                        if (e.getCause() instanceof IllegalArgumentException) {
                            return new Message(Map.of("numberTooBig", true), Map.of("_ErrorUnknown", Map.of()));
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
        var client = new Client(adapter, options);

        var dispatcher = connection.createDispatcher((msg) -> {
            try {
                var requestBytes = msg.getData();

                System.out.println("   ->C  %s".formatted(new String(requestBytes)));
                System.out.flush();

                var requestPseudoJson = objectMapper.readValue(requestBytes, List.class);
                var requestHeaders = (Map<String, Object>) requestPseudoJson.get(0);
                var requestBody = (Map<String, Object>) requestPseudoJson.get(1);
                var request = new Message(requestHeaders, requestBody);

                Message response;
                try (var time = timers.time()) {
                    response = client.request(request);
                }

                var responsePseudoJson = List.of(response.header, response.body);

                System.out.println(responsePseudoJson);

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

    public static Dispatcher startMockTestServer(Connection connection, MetricRegistry metrics, String apiSchemaPath,
            String frontdoorTopic,
            Map<String, Object> config)
            throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var uApi = UApiSchema.fromJson(json);

        var options = new MockServer.Options();
        options.onError = (e) -> e.printStackTrace();
        options.enableMessageResponseGeneration = false;

        if (config != null) {
            options.generatedCollectionLengthMin = (Integer) config.get("minLength");
            options.generatedCollectionLengthMax = (Integer) config.get("maxLength");
            options.enableMessageResponseGeneration = (Boolean) config.get("enableGen");
        }

        var timers = metrics.timer(frontdoorTopic);

        var server = new MockServer(uApi, options);

        var dispatcher = connection.createDispatcher((msg) -> {
            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();

            byte[] responseBytes;
            try (var time = timers.time()) {
                responseBytes = server.process(requestBytes);
            }

            System.out.println("    <-S %s".formatted(new String(responseBytes)));
            System.out.flush();

            connection.publish(msg.getReplyTo(), responseBytes);
        });
        dispatcher.subscribe(frontdoorTopic);

        return dispatcher;
    }

    public static Dispatcher startSchemaTestServer(Connection connection, MetricRegistry metrics, String apiSchemaPath,
            String frontdoorTopic)
            throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var uApi = UApiSchema.fromJson(json);
        var objectMapper = new ObjectMapper();

        var timers = metrics.timer(frontdoorTopic);

        Function<Message, Message> handler = (requestMessage) -> {
            var requestBody = requestMessage.body;

            var arg = (Map<String, Object>) requestBody.get("fn.validateSchema");
            var schemaPseudoJson = arg.get("schema");
            var extendSchemaJson = (String) arg.get("extend!");

            var serializeSchema = (Boolean) requestMessage.header.getOrDefault("_serializeSchema", true);

            String schemaJson;
            if (serializeSchema) {
                try {
                    var schemaJsonBytes = objectMapper.writeValueAsBytes(schemaPseudoJson);
                    schemaJson = new String(schemaJsonBytes);
                } catch (JsonProcessingException e) {
                    throw new RuntimeException(e);
                }
            } else {
                schemaJson = (String) schemaPseudoJson;
            }

            try {
                var schema = UApiSchema.fromJson(schemaJson);
                if (extendSchemaJson != null) {
                    UApiSchema.extend(schema, extendSchemaJson);
                }
                return new Message(Map.of(), Map.of("Ok", Map.of()));
            } catch (UApiSchemaParseError e) {
                e.printStackTrace();
                System.err.flush();
                return new Message(Map.of(),
                        Map.of("ErrorValidationFailure", Map.of("cases", e.schemaParseFailuresPseudoJson)));
            }
        };

        var options = new Server.Options();
        options.onError = (e) -> {
            e.printStackTrace();
            System.err.flush();
        };
        var server = new Server(uApi, handler, options);

        var dispatcher = connection.createDispatcher((msg) -> {
            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();

            byte[] responseBytes;
            try (var time = timers.time()) {
                responseBytes = server.process(requestBytes);
            }

            System.out.println("    <-S %s".formatted(new String(responseBytes)));
            System.out.flush();

            connection.publish(msg.getReplyTo(), responseBytes);
        });
        dispatcher.subscribe(frontdoorTopic);

        return dispatcher;
    }

    public static Dispatcher startTestServer(Connection connection, MetricRegistry metrics, String apiSchemaPath,
            String frontdoorTopic,
            String backdoorTopic)
            throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var uApi = UApiSchema.fromJson(json);
        var alternateUApi = UApiSchema.extend(uApi, """
                [
                    {
                        "struct.BackwardsCompatibleChange": {}
                    }
                ]
                """);
        var objectMapper = new ObjectMapper();

        var timers = metrics.timer(frontdoorTopic);

        var serveAlternateServer = new AtomicBoolean();

        class ThisError extends RuntimeException {
        }

        Function<Message, Message> handler = (requestMessage) -> {
            try {
                var requestHeaders = requestMessage.header;
                var requestBody = requestMessage.body;
                var requestPseudoJson = List.of(requestHeaders, requestBody);
                var requestBytes = objectMapper.writeValueAsBytes(requestPseudoJson);

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

                var toggleAlternateServer = requestHeaders.get("_toggleAlternateServer");
                if (Objects.equals(true, toggleAlternateServer)) {
                    serveAlternateServer.set(!serveAlternateServer.get());
                }

                var throwError = requestHeaders.get("_throwError");
                if (Objects.equals(true, throwError)) {
                    throw new ThisError();
                }

                return new Message(responseHeaders, responseBody);
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
            if ((Boolean) m.header.getOrDefault("_onRequestError", false)) {
                throw new RuntimeException();
            }
        };
        options.onResponse = m -> {
            if ((Boolean) m.header.getOrDefault("_onResponseError", false)) {
                throw new RuntimeException();
            }
        };

        var server = new Server(uApi, handler, options);

        var alternateOptions = new Server.Options();
        alternateOptions.onError = (e) -> e.printStackTrace();

        var alternateServer = new Server(alternateUApi, handler, alternateOptions);

        var dispatcher = connection.createDispatcher((msg) -> {

            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();

            byte[] responseBytes;
            try (var time = timers.time()) {
                if (serveAlternateServer.get()) {
                    responseBytes = alternateServer.process(requestBytes);
                } else {
                    responseBytes = server.process(requestBytes);
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

                            var d = startTestServer(connection, metrics, apiSchemaPath, frontdoorTopic,
                                    backdoorTopic);

                            servers.put(id, d);
                        }
                        case "StartClientServer" -> {
                            var id = (String) payload.get("id");
                            var clientFrontdoorTopic = (String) payload.get("clientFrontdoorTopic");
                            var clientBackdoorTopic = (String) payload.get("clientBackdoorTopic");
                            var useBinary = (Boolean) payload.getOrDefault("useBinary", false);

                            var d = startClientTestServer(connection, metrics, clientFrontdoorTopic,
                                    clientBackdoorTopic,
                                    useBinary);

                            servers.put(id, d);
                        }
                        case "StartMockServer" -> {
                            var id = (String) payload.get("id");
                            var apiSchemaPath = (String) payload.get("apiSchemaPath");
                            var frontdoorTopic = (String) payload.get("frontdoorTopic");
                            var config = (Map<String, Object>) payload.get("config");
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

                    responseBytes = objectMapper.writeValueAsBytes(List.of(Map.of(), Map.of("Ok", Map.of())));
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

            metricsReporter.report();

            System.out.println("Dispatcher exiting");
        }
    }

    @Test
    public void test() throws InterruptedException, IOException {
        runDispatcherServer();
    }
}
