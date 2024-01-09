package io.github.brenbar.japi;

import java.io.IOException;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.ReentrantLock;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.nats.client.Dispatcher;
import io.nats.client.Nats;

public class TestDispatch {

    @Test
    public void runDispatcher() throws InterruptedException, IOException {
        var natsUrl = "nats://127.0.0.1:4222";
        var objectMapper = new ObjectMapper();

        var lock = new ReentrantLock();
        var done = lock.newCondition();

        var servers = new HashMap<String, Dispatcher>();
        try (var connection = Nats.connect(natsUrl)) {
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

                            var d = TestServer.start(connection, apiSchemaPath, frontdoorTopic, backdoorTopic);

                            servers.put(id, d);
                        }
                        case "StartClientServer" -> {
                            var id = (String) payload.get("id");
                            var clientFrontdoorTopic = (String) payload.get("clientFrontdoorTopic");
                            var clientBackdoorTopic = (String) payload.get("clientBackdoorTopic");
                            var useBinary = (Boolean) payload.getOrDefault("useBinary", false);

                            var d = ClientTestServer.start(connection, clientFrontdoorTopic, clientBackdoorTopic,
                                    useBinary);

                            servers.put(id, d);
                        }
                        case "StartMockServer" -> {
                            var id = (String) payload.get("id");
                            var apiSchemaPath = (String) payload.get("apiSchemaPath");
                            var frontdoorTopic = (String) payload.get("frontdoorTopic");
                            var d = MockTestServer.start(connection, apiSchemaPath, frontdoorTopic);

                            servers.put(id, d);
                        }
                        case "StartSchemaServer" -> {
                            var id = (String) payload.get("id");
                            var apiSchemaPath = (String) payload.get("apiSchemaPath");
                            var frontdoorTopic = (String) payload.get("frontdoorTopic");
                            var d = SchemaTestServer.start(connection, apiSchemaPath, frontdoorTopic);

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

            System.out.println("Dispatcher exiting");
        }
    }
}
