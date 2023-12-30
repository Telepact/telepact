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
import io.nats.client.Nats;

public class TestServer {

    public static void main(String[] givenArgs) throws IOException, InterruptedException {
        var args = givenArgs[0].split(",");
        var apiSchemaPath = args[0];
        var natsUrl = args[1];
        var frontdoorTopic = args[2];
        var backdoorTopic = args[3];

        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var jApi = new JApiSchema(json);
        var alternateJApi = new JApiSchema(jApi, new JApiSchema("""
                [
                    {
                        "struct.BackwardsCompatibleChange": {}
                    }
                ]
                """));
        var objectMapper = new ObjectMapper();

        System.out.println(alternateJApi.original);

        var serveAlternateServer = new AtomicBoolean();

        try (var connection = Nats.connect(natsUrl)) {

            Function<Message, Message> handler = (requestMessage) -> {
                try {
                    var requestHeaders = requestMessage.header;
                    var requestBody = requestMessage.body;
                    var requestPseudoJson = List.of(requestHeaders, requestBody);
                    var requestBytes = objectMapper.writeValueAsBytes(requestPseudoJson);

                    System.out.println("   <-|  %s".formatted(new String(requestBytes)));
                    System.out.flush();

                    io.nats.client.Message natsResponseMessage;
                    try {
                        natsResponseMessage = connection.request(backdoorTopic, requestBytes, Duration.ofSeconds(5));
                    } catch (InterruptedException e1) {
                        throw new RuntimeException("Interruption");
                    }
                    var responseBytes = natsResponseMessage.getData();

                    System.out.println("   ->|  %s".formatted(new String(responseBytes)));
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

            var server = new Server(jApi, handler, new Options().setOnError((e) -> e.printStackTrace()));
            var alternateServer = new Server(alternateJApi, handler,
                    new Options().setOnError((e) -> e.printStackTrace()));

            var dispatcher = connection.createDispatcher((msg) -> {
                var requestBytes = msg.getData();

                System.out.println("    ->| %s".formatted(new String(requestBytes)));
                System.out.flush();
                byte[] responseBytes;
                if (serveAlternateServer.get()) {
                    responseBytes = alternateServer.process(requestBytes);
                } else {
                    responseBytes = server.process(requestBytes);
                }
                System.out.println("    <-| %s".formatted(new String(responseBytes)));
                System.out.flush();

                connection.publish(msg.getReplyTo(), responseBytes);
            });

            dispatcher.subscribe(frontdoorTopic);

            Files.write(Path.of("SERVER_READY"), "".getBytes(), StandardOpenOption.CREATE);
            Thread.sleep(10000000);
        }
    }
}
