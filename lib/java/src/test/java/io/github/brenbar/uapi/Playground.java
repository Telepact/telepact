package io.github.brenbar.uapi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.Map;
import java.util.function.Function;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import uapi.Message;
import uapi.Server;
import uapi.UApiSchema;
import uapi.UApiSchemaParseError;

public class Playground {
    public static void main(String[] args) throws IOException {
        var json = Files.readString(FileSystems.getDefault().getPath("../../qa/test",
                "binary.uapi.json"));
        var uApi = UApiSchema.fromJson(json);
        System.out.println("Done!");

        var objectMapper = new ObjectMapper();

        Function<Message, Message> handler = (requestMessage) -> {
            var requestBody = requestMessage.body;

            var arg = (Map<String, Object>) requestBody.get("fn.validateSchema");
            var schemaPseudoJson = arg.get("schema");
            var extendSchemaJson = (String) arg.get("extend!");

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
                var schema = UApiSchema.fromJson(schemaJson);
                if (extendSchemaJson != null) {
                    UApiSchema.extend(schema, extendSchemaJson);
                }
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            } catch (UApiSchemaParseError e) {
                e.printStackTrace();
                System.err.flush();
                return new Message(Map.of(),
                        Map.of("ErrorValidationFailure", Map.of("cases", e.schemaParseFailuresPseudoJson)));
            }
        };

        var options = new Server.Options();
        options.authRequired = false;
        var server = new Server(uApi, handler, options);

        var result = server.process(
                """
                        [{"bin_": [{}]}, {"fn.ping_": {}}]
                                """
                        .getBytes());

        System.out.println(new String(result));

        // server.process(
        // """
        // [{}, {"fn.validateSchema": {"schema": [{"requestHeader.field": ["boolean"]},
        // {"requestHeader.field": ["integer"]}]}}]
        // """
        // .getBytes());

        // BiFunction<Message, Serializer, Future<Message>> adapter = (m, s) -> {
        // return CompletableFuture.supplyAsync(() -> {
        // var requestBytes = s.serialize(m);
        // var responseBytes = server.process(requestBytes);
        // return s.deserialize(responseBytes);
        // });
        // };

        // var clientOptions = new Client.Options();
        // clientOptions.useBinary = true;
        // clientOptions.timeoutMsDefault = 100000000000L;
        // var client = new Client(adapter, clientOptions);
        // var result = client
        // .request(new Message(Map.of(), Map.of("fn.test", Map.of("value!",
        // Map.of("pStrBool!",
        // Map.of("wrap", 0))))));
        // System.out.println(result.body);

        // var r = new _RandomGenerator(3, 3);
        // for (var i = 0; i < 100; i += 1) {
        // r.nextInt();
        // System.out.println(r.seed);
        // }
    }
}
