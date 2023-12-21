package io.github.brenbar.japi;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.Map;
import java.util.function.Function;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;

public class SchemaTestServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        var socketPath = "./frontdoor.socket";

        var path = args[0];
        var json = Files.readString(FileSystems.getDefault().getPath(path));
        var jApi = new JApiSchema(json);
        var objectMapper = new ObjectMapper();

        Function<Message, Message> handler = (requestMessage) -> {
            var requestBody = requestMessage.body;

            var arg = (Map<String, Object>) requestBody.get("fn.validateSchema");
            var schemaPseudoJson = arg.get("schema");

            byte[] schemaJson;
            try {
                schemaJson = objectMapper.writeValueAsBytes(schemaPseudoJson);
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }

            try {
                var schema = new JApiSchema(new String(schemaJson));
                return new Message(Map.of(), Map.of("ok", Map.of()));
            } catch (JApiSchemaParseError e) {
                return new Message(Map.of(),
                        Map.of("errorValidationFailure", Map.of("cases", e.schemaParseFailuresPseudoJson)));
            }
        };

        var server = new Server(jApi, handler, new Options().setOnError((e) -> e.printStackTrace()));

        var socket = UnixDomainSocketAddress.of(socketPath);
        Files.deleteIfExists(socket.getPath());
        try (var serverChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)) {
            serverChannel.bind(socket);
            while (true) {
                try (var clientChannel = serverChannel.accept()) {
                    var requestBytes = TestUtility.readSocket(clientChannel);

                    System.out.println("    ->| %s".formatted(new String(requestBytes)));
                    var responseBytes = server.process(requestBytes);
                    System.out.println("    <-| %s".formatted(new String(responseBytes)));

                    TestUtility.writeSocket(clientChannel, responseBytes);
                }
            }
        }
    }
}
