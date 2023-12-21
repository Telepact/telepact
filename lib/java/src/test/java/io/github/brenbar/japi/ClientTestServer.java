package io.github.brenbar.japi;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Client.Adapter;
import io.github.brenbar.japi.Client.Options;

public class ClientTestServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        var socketPath = "./clientfrontdoor.socket";
        var socketBackdoorPath = "./clientbackdoor.socket";

        var objectMapper = new ObjectMapper();

        var backdoorSocket = UnixDomainSocketAddress.of(socketBackdoorPath);

        Adapter adapter = (m, s) -> {
            return CompletableFuture.supplyAsync(() -> {
                try (var backdoorChannel = SocketChannel.open(backdoorSocket)) {
                    var requestBytes = s.serialize(m);

                    System.out.println("|>    %s".formatted(new String(requestBytes)));

                    TestUtility.writeSocket(backdoorChannel, requestBytes);

                    var responseBytes = TestUtility.readSocket(backdoorChannel);

                    System.out.println("|<    %s".formatted(new String(responseBytes)));

                    var responseMessage = s.deserialize(responseBytes);
                    return responseMessage;
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });
        };

        var client = new Client(adapter, new Options());

        var socket = UnixDomainSocketAddress.of(socketPath);
        Files.deleteIfExists(socket.getPath());
        try (var serverChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)) {
            serverChannel.bind(socket);
            while (true) {
                try (var clientChannel = serverChannel.accept()) {
                    var requestBytes = TestUtility.readSocket(clientChannel);

                    System.out.println("|<--  %s".formatted(new String(requestBytes)));

                    var requestPseudoJson = objectMapper.readValue(requestBytes, List.class);
                    var requestHeaders = (Map<String, Object>) requestPseudoJson.get(0);
                    var requestBody = (Map<String, Object>) requestPseudoJson.get(1);
                    var request = new Message(requestHeaders, requestBody);

                    var response = client.send(request);
                    var responsePseudoJson = List.of(response.header, response.header);
                    var responseBytes = objectMapper.writeValueAsBytes(responsePseudoJson);

                    System.out.println("|-->  %s".formatted(new String(responseBytes)));

                    TestUtility.writeSocket(clientChannel, responseBytes);
                }
            }
        }
    }
}
