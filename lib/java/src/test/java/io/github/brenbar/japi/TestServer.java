package io.github.brenbar.japi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.OpenOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Function;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;
import io.nats.client.Nats;

public class TestServer {

    public static Dispatcher start(Connection connection, String apiSchemaPath, String frontdoorTopic,
            String backdoorTopic)
            throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var jApi = JApiSchema.fromJson(json);
        var alternateJApi = JApiSchema.extend(jApi, """
                [
                    {
                        "struct.BackwardsCompatibleChange": {}
                    }
                ]
                """);
        var objectMapper = new ObjectMapper();

        var serveAlternateServer = new AtomicBoolean();

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
                } catch (InterruptedException e1) {
                    throw new RuntimeException("Interruption");
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

                return new Message(responseHeaders, responseBody);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };

        var server = new Server(jApi, handler, new Options().setOnError((e) -> {
            e.printStackTrace();
            System.err.flush();
        }).setOnRequest(m -> {
            if ((Boolean) m.header.getOrDefault("_onRequestError", false)) {
                throw new RuntimeException();
            }
        }).setOnResponse(m -> {
            if ((Boolean) m.header.getOrDefault("_onResponseError", false)) {
                throw new RuntimeException();
            }
        }));
        var alternateServer = new Server(alternateJApi, handler,
                new Options().setOnError((e) -> e.printStackTrace()));

        var dispatcher = connection.createDispatcher((msg) -> {
            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();
            byte[] responseBytes;
            if (serveAlternateServer.get()) {
                responseBytes = alternateServer.process(requestBytes);
            } else {
                responseBytes = server.process(requestBytes);
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
