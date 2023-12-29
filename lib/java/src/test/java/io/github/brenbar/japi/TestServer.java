package io.github.brenbar.japi;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;

public class TestServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        var socketPath = "./frontdoor.socket";
        var socketBackdoorPath = "./backdoor.socket";

        var path = args[0];
        var json = Files.readString(FileSystems.getDefault().getPath(path));
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

        var backdoorSocket = UnixDomainSocketAddress.of(socketBackdoorPath);

        var serveAlternateServer = new AtomicBoolean();

        Function<Message, Message> handler = (requestMessage) -> {
            try (var backdoorChannel = SocketChannel.open(backdoorSocket)) {
                var requestHeaders = requestMessage.header;
                var requestBody = requestMessage.body;
                var requestPseudoJson = List.of(requestHeaders, requestBody);
                var requestBytes = objectMapper.writeValueAsBytes(requestPseudoJson);

                System.out.println("   <-|  %s".formatted(new String(requestBytes)));
                System.out.flush();

                TestUtility.writeSocket(backdoorChannel, requestBytes);

                var responseBytes = TestUtility.readSocket(backdoorChannel);

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
        var alternateServer = new Server(alternateJApi, handler, new Options().setOnError((e) -> e.printStackTrace()));

        var socket = UnixDomainSocketAddress.of(socketPath);
        Files.deleteIfExists(socket.getPath());
        try (var serverChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)) {
            serverChannel.bind(socket);
            while (true) {
                try (var clientChannel = serverChannel.accept()) {
                    var requestBytes = TestUtility.readSocket(clientChannel);

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

                    TestUtility.writeSocket(clientChannel, responseBytes);
                }
            }
        }
    }
}
