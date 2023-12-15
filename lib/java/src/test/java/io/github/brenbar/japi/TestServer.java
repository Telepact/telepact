package io.github.brenbar.japi;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.ServerSocketChannel;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;

public class TestServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        var socketAddress = UnixDomainSocketAddress.of("./testServer.socket");
        var serverSocketChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX);
        serverSocketChannel.bind(socketAddress);

        try (var serverChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)) {
            serverChannel.bind(socketAddress);
            try (var clientChannel = serverSocketChannel.accept()) {

                var path = args[0];
                var json = Files.readString(FileSystems.getDefault().getPath(path));
                var jApi = new JApiSchema(json);
                var objectMapper = new ObjectMapper();

                Function<Message, Message> handler = (requestMessage) -> {
                    try {
                        var requestHeaders = requestMessage.header;
                        var requestBody = requestMessage.body;
                        var requestPseudoJson = List.of(requestHeaders, requestBody);
                        var requestBytes = objectMapper.writeValueAsBytes(requestPseudoJson);

                        var requestBuf = ByteBuffer.allocate(requestBytes.length);
                        requestBuf.put(requestBytes);
                        clientChannel.write(requestBuf);

                        var responseBuf = ByteBuffer.allocate(1024);
                        while (clientChannel.read(responseBuf) == 0)
                            ;

                        var responseBytes = responseBuf.array();
                        var responsePseudoJson = objectMapper.readValue(responseBytes, List.class);
                        var responseHeaders = (Map<String, Object>) responsePseudoJson.get(0);
                        var responseBody = (Map<String, Object>) responsePseudoJson.get(1);
                        return new Message(responseHeaders, responseBody);
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                };

                var server = new Server(jApi, handler, new Options().setOnError((e) -> e.printStackTrace()));

                while (true) {
                    var readBuf = ByteBuffer.allocate(1024);
                    var bytesRead = clientChannel.read(readBuf);
                    if (bytesRead == 0) {
                        Thread.sleep(1);
                    }
                    readBuf.flip();
                    var requestBytes = readBuf.array();

                    var responseBytes = server.process(requestBytes);

                    var responseBuf = ByteBuffer.allocate(responseBytes.length);
                    responseBuf.put(responseBytes);
                    clientChannel.write(responseBuf);
                }
            }
        } finally {
            Files.deleteIfExists(socketAddress.getPath());
        }
    }
}
