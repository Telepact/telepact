package io.github.brenbar.uapi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;

import com.codahale.metrics.MetricRegistry;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.uapi.Server.Options;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;

public class TestServer {

    public static Dispatcher start(Connection connection, MetricRegistry metrics, String apiSchemaPath,
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

        var options = new Options();
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

        var alternateOptions = new Options();
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
}
