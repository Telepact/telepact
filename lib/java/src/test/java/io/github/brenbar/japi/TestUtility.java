package io.github.brenbar.japi;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Client.Adapter;
import io.github.brenbar.japi.Server.Options;

public class TestUtility {

    private static Message handle(Message requestMessage) {
        var requestHeaders = requestMessage.header;
        var functionName = requestMessage.body.keySet().stream().findAny().get();
        return switch (functionName) {
            case "fn.test" -> {
                if (requestHeaders.containsKey("ok")) {
                    try {
                        var o = (Map<String, Object>) requestHeaders.get("ok");
                        yield new Message(Map.of("ok", o));
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                } else if (requestHeaders.containsKey("result")) {
                    try {
                        var r = (Map<String, Object>) requestHeaders.get("result");
                        yield new Message(r);
                    } catch (ClassCastException e) {
                        throw new RuntimeException(e);
                    }
                } else if (Objects.equals(true, requestHeaders.get("throw"))) {
                    throw new RuntimeException();
                } else {
                    yield new Message(Map.of());
                }
            }
            default -> throw new RuntimeException();
        };

    }

    public static void test(String requestJson, String expectedResponseJson) throws IOException {
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var server = new Server(json, TestUtility::handle, new Options().setOnError((e) -> e.printStackTrace()));
        var expectedResponseAsParsedJson = objectMapper.readValue(expectedResponseJson,
                new TypeReference<List<Object>>() {
                });

        // test json
        {
            var requestBytes = requestJson.getBytes(StandardCharsets.UTF_8);
            System.out.println("--> %s".formatted(new String(requestBytes)));
            var responseBytes = server.process(requestBytes);
            System.out.println("<-- %s".formatted(new String(responseBytes)));
            var responseAsParsedJson = objectMapper.readValue(responseBytes, new TypeReference<List<Object>>() {
            });
            assertEquals(expectedResponseAsParsedJson, responseAsParsedJson);
        }
    }

    public static void testBinary(String requestJson, String expectedResponseJson) throws IOException {
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var server = new Server(json, TestUtility::handle, new Options().setOnError((e) -> e.printStackTrace()));
        var expectedResponseAsParsedJson = objectMapper.readValue(expectedResponseJson,
                new TypeReference<List<Object>>() {
                });

        // test binary
        {
            Adapter adapter = (m, s) -> {
                return CompletableFuture.supplyAsync(() -> {
                    var requestBytes = s.serialize(m);
                    System.out.println("--> %s".formatted(new String(requestBytes)));
                    var responseBytes = server.process(requestBytes);
                    System.out.println("<-- %s".formatted(new String(responseBytes)));
                    Message response = s.deserialize(responseBytes);
                    return response;
                });
            };
            var client = new Client(adapter,
                    new Client.Options().setForceSendJsonDefault(false).setUseBinaryDefault(true)
                            .setTimeoutMsDefault(600000));
            client.send(client.createRequestMessage(new Request("fn._ping", Map.of()))); // warmup
            var requestAsParsedJson = objectMapper.readValue(requestJson, new TypeReference<List<Object>>() {
            });

            var requestHeadersPseudoJson = (Map<String, Object>) requestAsParsedJson.get(0);
            var requestBodyPseudoJson = (Map<String, Object>) requestAsParsedJson.get(1);
            var requestTargetPseudoJson = requestBodyPseudoJson.keySet().stream().findAny().get();
            var requestPayloadPseudoJson = (Map<String, Object>) requestBodyPseudoJson.values().stream().findAny()
                    .get();

            var responseMessage = client.send(client.createRequestMessage(new Request(requestTargetPseudoJson,
                    requestPayloadPseudoJson).addHeaders(
                            requestHeadersPseudoJson)));
            var resultAsPseudoJson = responseMessage.body;
            assertEquals(expectedResponseAsParsedJson.get(1), resultAsPseudoJson);
        }
    }

    public static void testBinaryExact(byte[] requestBytes, String expectedResponseJson) throws IOException {
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var server = new Server(json, TestUtility::handle, new Options().setOnError((e) -> e.printStackTrace()));
        var expectedResponseAsParsedJson = objectMapper.readValue(expectedResponseJson,
                new TypeReference<List<Object>>() {
                });

        // test json
        {
            System.out.println("--> %s".formatted(new String(requestBytes)));
            var responseBytes = server.process(requestBytes);
            System.out.println("<-- %s".formatted(new String(responseBytes)));
            var responseAsParsedJson = objectMapper.readValue(responseBytes, new TypeReference<List<Object>>() {
            });
            assertEquals(expectedResponseAsParsedJson, responseAsParsedJson);
        }
    }

    public static MockServer generatedMockTestSetup() throws IOException {
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var server = new MockServer(json,
                new io.github.brenbar.japi.MockServer.Options().setOnError((e) -> e.printStackTrace())
                        .setEnableGeneratedDefaultStub(false));
        return server;
    }

    public static void generatedMockTest(String requestJson, String expectedResponseJson, MockServer server)
            throws IOException {
        var objectMapper = new ObjectMapper();
        var expectedResponseAsParsedJson = objectMapper.readValue(expectedResponseJson,
                new TypeReference<List<Object>>() {
                });
        var requestBytes = requestJson.getBytes(StandardCharsets.UTF_8);
        System.out.println("--> %s".formatted(new String(requestBytes)));
        var responseBytes = server.process(requestBytes);
        System.out.println("<-- %s".formatted(new String(responseBytes)));
        var responseAsParsedJson = objectMapper.readValue(responseBytes, new TypeReference<List<Object>>() {
        });
        assertEquals(expectedResponseAsParsedJson, responseAsParsedJson);
    }

}
