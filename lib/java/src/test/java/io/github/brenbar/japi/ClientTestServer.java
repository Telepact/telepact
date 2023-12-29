package io.github.brenbar.japi;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.file.Files;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.function.Function;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Client.Adapter;
import io.github.brenbar.japi.Client.Options;
import io.nats.client.Nats;

public class ClientTestServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        var natsUrl = args[0];
        var clientFrontdoorTopic = args[1];
        var clientBackdoorTopic = args[2];

        var objectMapper = new ObjectMapper();

        try (var connection = Nats.connect(natsUrl)) {

            Adapter adapter = (m, s) -> {
                return CompletableFuture.supplyAsync(() -> {
                    try {
                        byte[] requestBytes;
                        try {
                            requestBytes = s.serialize(m);
                        } catch (IllegalArgumentException e) {
                            return new Message(Map.of("numberTooBig", true), Map.of("_ErrorUnknown", Map.of()));
                        }

                        System.out.println("  <-|   %s".formatted(new String(requestBytes)));
                        System.out.flush();

                        io.nats.client.Message natsResponseMessage;
                        try {
                            natsResponseMessage = connection.request(clientBackdoorTopic, requestBytes,
                                    Duration.ofSeconds(5));
                        } catch (InterruptedException e1) {
                            throw new RuntimeException("Interruption");
                        }
                        var responseBytes = natsResponseMessage.getData();

                        System.out.println("  ->|   %s".formatted(new String(responseBytes)));
                        System.out.flush();

                        var responseMessage = s.deserialize(responseBytes);
                        return responseMessage;
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                });
            };

            var client = new Client(adapter, new Options());

            var dispatcher = connection.createDispatcher((msg) -> {
                try {
                    var requestBytes = msg.getData();

                    System.out.println("    ->| %s".formatted(new String(requestBytes)));
                    System.out.flush();

                    var requestPseudoJson = objectMapper.readValue(requestBytes, List.class);
                    var requestHeaders = (Map<String, Object>) requestPseudoJson.get(0);
                    var requestBody = (Map<String, Object>) requestPseudoJson.get(1);
                    var request = new Message(requestHeaders, requestBody);

                    var response = client.send(request);

                    var responsePseudoJson = List.of(response.header, response.body);
                    var responseBytes = objectMapper.writeValueAsBytes(responsePseudoJson);

                    System.out.println("    <-| %s".formatted(new String(responseBytes)));
                    System.out.flush();

                    connection.publish(msg.getReplyTo(), responseBytes);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });
            dispatcher.subscribe(clientFrontdoorTopic);
        }
    }
}
