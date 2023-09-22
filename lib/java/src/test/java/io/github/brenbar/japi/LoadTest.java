package io.github.brenbar.japi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

import com.codahale.metrics.ConsoleReporter;
import com.codahale.metrics.MetricRegistry;

import io.github.brenbar.japi.Client.Adapter;
import io.nats.client.Nats;

public class LoadTest {

    @Test
    @Disabled("Test preserved for record")
    public void test() throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "calculator.japi.json"));

        var server = new MockServer(json)
                .setOnError((e) -> e.printStackTrace())
                .setEnableGeneratedDefaultStub(true);

        var natsUrl = "nats://127.0.0.1:4222";

        var metrics = new MetricRegistry();
        var metricsReporter = ConsoleReporter.forRegistry(metrics).build();

        var binarySize = metrics.histogram("size-binary");
        var jsonSize = metrics.histogram("size-json");

        try (var connection = Nats.connect(natsUrl)) {

            var dispatcher = connection.createDispatcher((msg) -> {
                var requestBytes = msg.getData();
                var responseBytes = server.process(requestBytes);
                connection.publish(msg.getReplyTo(), responseBytes);
            });
            dispatcher.subscribe("example-api");

            Adapter adapter = (m, s) -> {
                return CompletableFuture.supplyAsync(() -> {
                    var requestBytes = s.serialize(m);

                    System.out.println("--> %s".formatted(new String(requestBytes)));
                    io.nats.client.Message responseMessage;
                    try {
                        responseMessage = connection.request("example-api", requestBytes, Duration.ofSeconds(5));
                    } catch (InterruptedException e1) {
                        throw new RuntimeException("Interruption");
                    }
                    var responseBytes = responseMessage.getData();

                    if (Objects.equals(((Map<String, Object>) m.get(1)).get("b"), true)) {
                        binarySize.update(responseBytes.length);
                    } else {
                        jsonSize.update(responseBytes.length);
                    }

                    System.out.println("<-- %s".formatted(new String(responseBytes)));
                    List<Object> response = s.deserialize(responseBytes);
                    var header = (Map<String, Object>) response.get(0);
                    var body = (Map<String, Map<String, Object>>) response.get(1);
                    return new Message(header, body);
                });
            };

            var client = new Client(adapter).setForceSendJsonDefault(false).setUseBinaryDefault(true)
                    .setTimeoutMsDefault(600000);

            // warmup
            client.request(new Request("fn.getPaperTape", Map.of()));

            var jsonTimers = metrics.timer("roundtrip-json");

            for (int i = 0; i < 25; i += 1) {
                try (var time = jsonTimers.time()) {
                    client.request(new Request("fn.getPaperTape", Map.of()).setUseBinary(false));
                }
            }

            var binaryTimers = metrics.timer("roundtrip-binary");

            for (int i = 0; i < 25; i += 1) {
                try (var time = binaryTimers.time()) {
                    client.request(new Request("fn.getPaperTape", Map.of()).addHeader("b", true));
                }
            }

        }

        metricsReporter.report();

    }

}
