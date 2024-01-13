package io.github.brenbar.japi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.Map;
import java.util.function.Function;

import com.codahale.metrics.MetricRegistry;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;
import io.nats.client.Connection;
import io.nats.client.Dispatcher;

public class SchemaTestServer {

    public static Dispatcher start(Connection connection, MetricRegistry metrics, String apiSchemaPath,
            String frontdoorTopic)
            throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var jApi = JApiSchema.fromJson(json);
        var objectMapper = new ObjectMapper();

        var timers = metrics.timer(frontdoorTopic);

        Function<Message, Message> handler = (requestMessage) -> {
            var requestBody = requestMessage.body;

            var arg = (Map<String, Object>) requestBody.get("fn.validateSchema");
            var schemaPseudoJson = arg.get("schema");

            var serializeSchema = (Boolean) requestMessage.header.getOrDefault("_serializeSchema", true);

            String schemaJson;
            if (serializeSchema) {
                try {
                    var schemaJsonBytes = objectMapper.writeValueAsBytes(schemaPseudoJson);
                    schemaJson = new String(schemaJsonBytes);
                } catch (JsonProcessingException e) {
                    throw new RuntimeException(e);
                }
            } else {
                schemaJson = (String) schemaPseudoJson;
            }

            try {
                var schema = JApiSchema.fromJson(schemaJson);
                return new Message(Map.of(), Map.of("Ok", Map.of()));
            } catch (JApiSchemaParseError e) {
                e.printStackTrace();
                System.err.flush();
                return new Message(Map.of(),
                        Map.of("ErrorValidationFailure", Map.of("cases", e.schemaParseFailuresPseudoJson)));
            }
        };

        var server = new Server(jApi, handler, new Options().setOnError((e) -> {
            e.printStackTrace();
            System.err.flush();
        }));

        var dispatcher = connection.createDispatcher((msg) -> {
            var requestBytes = msg.getData();

            System.out.println("    ->S %s".formatted(new String(requestBytes)));
            System.out.flush();

            byte[] responseBytes;
            try (var time = timers.time()) {
                responseBytes = server.process(requestBytes);
            }

            System.out.println("    <-S %s".formatted(new String(responseBytes)));
            System.out.flush();

            connection.publish(msg.getReplyTo(), responseBytes);
        });
        dispatcher.subscribe(frontdoorTopic);

        return dispatcher;
    }
}
