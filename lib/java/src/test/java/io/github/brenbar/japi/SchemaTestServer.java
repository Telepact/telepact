package io.github.brenbar.japi;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;
import io.nats.client.Nats;

public class SchemaTestServer {

    public static void main(String[] givenArgs) throws IOException, InterruptedException {
        var args = givenArgs[0].split(",");
        var apiSchemaPath = args[0];
        var natsUrl = args[1];
        var frontdoorTopic = args[2];

        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
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
                return new Message(Map.of(), Map.of("Ok", Map.of()));
            } catch (JApiSchemaParseError e) {
                return new Message(Map.of(),
                        Map.of("errorValidationFailure", Map.of("cases", e.schemaParseFailuresPseudoJson)));
            }
        };

        var server = new Server(jApi, handler, new Options().setOnError((e) -> e.printStackTrace()));

        try (var connection = Nats.connect(natsUrl)) {
            var dispatcher = connection.createDispatcher((msg) -> {
                var requestBytes = msg.getData();

                System.out.println("    ->S %s".formatted(new String(requestBytes)));
                System.out.flush();
                var responseBytes = server.process(requestBytes);
                System.out.println("    <-S %s".formatted(new String(responseBytes)));
                System.out.flush();

                connection.publish(msg.getReplyTo(), responseBytes);
            });
            dispatcher.subscribe(frontdoorTopic);

            Files.write(Path.of("SCHEMA_SERVER_READY"), "".getBytes(), StandardOpenOption.CREATE);
            Thread.sleep(10000000);
        }
    }
}
