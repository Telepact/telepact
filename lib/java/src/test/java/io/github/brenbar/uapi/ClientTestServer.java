package io.github.brenbar.uapi;

import java.io.IOException;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.function.BiFunction;

import com.codahale.metrics.MetricRegistry;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.uapi.Client.Options;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;

public class ClientTestServer {

    public static Dispatcher start(Connection connection, MetricRegistry metrics, String clientFrontdoorTopic,
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
                    } catch (RuntimeException e) {
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

        var options = new Options();
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
}
