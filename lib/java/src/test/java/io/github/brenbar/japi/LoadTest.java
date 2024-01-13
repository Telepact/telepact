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
import io.github.brenbar.japi.MockServer.Options;
import io.nats.client.Nats;

public class LoadTest {

    @Test
    @Disabled("Test preserved for record")
    public void test() throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "calculator.japi.json"));

        var jApiSchema = JApiSchema.fromJson(json);

        var options = new Options();
        options.onError = (e) -> e.printStackTrace();
        options.enableGeneratedDefaultStub = true;
        var server = new MockServer(jApiSchema, options);

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

                    if (Objects.equals(((Map<String, Object>) m.body).get("b"), true)) {
                        binarySize.update(responseBytes.length);
                    } else {
                        jsonSize.update(responseBytes.length);
                    }

                    System.out.println("<-- %s".formatted(new String(responseBytes)));
                    return s.deserialize(responseBytes);
                });
            };

            var clientOptions = new Client.Options();
            clientOptions.useBinaryDefault = false;
            clientOptions.timeoutMsDefault = 600000;

            var client = new Client(adapter, clientOptions);

            // warmup
            var requestMessage = new Message("fn.getPaperTape", Map.of());
            client.send(requestMessage);

            var jsonTimers = metrics.timer("roundtrip-json");

            for (int i = 0; i < 25; i += 1) {
                try (var time = jsonTimers.time()) {
                    var requestMessage2 = new Message("fn.getPaperTape", Map.of());
                    client.send(requestMessage2);
                }
            }

            var binaryTimers = metrics.timer("roundtrip-binary");

            for (int i = 0; i < 25; i += 1) {
                try (var time = binaryTimers.time()) {
                    var requestMessage3 = new Message(Map.of("_binary", true), Map.of("fn.getPaperTape", Map.of()));
                    client.send(requestMessage3);
                }
            }

        }

        metricsReporter.report();

    }

}
