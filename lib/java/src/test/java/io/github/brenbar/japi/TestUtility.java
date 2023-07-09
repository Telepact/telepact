package io.github.brenbar.japi;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Client.Adapter;

public class TestUtility {

    private static Map<String, Object> handle(Context context, Map<String, Object> body) {
        return switch (context.functionName) {
            case "test" -> {
                var error = context.requestHeaders.keySet().stream().filter(k -> k.startsWith("error.")).findFirst();
                if (context.requestHeaders.containsKey("output")) {
                    try {
                        var o = (Map<String, Object>) context.requestHeaders.get("output");
                        yield o;
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                } else if (error.isPresent()) {
                    try {
                        var e = (Map<String, Object>) context.requestHeaders.get(error.get());
                        throw new JApiError(error.get(), e);
                    } catch (ClassCastException e) {
                        throw new RuntimeException(e);
                    }
                } else {
                    yield Map.of();
                }
            }
            default -> throw new RuntimeException();
        };
    }

    public static void test(String requestJson, String expectedResponseJson) throws IOException {
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var processor = new Server(json, TestUtility::handle).setOnError((e) -> e.printStackTrace());
        var expectedResponseAsParsedJson = objectMapper.readValue(expectedResponseJson,
                new TypeReference<List<Object>>() {
                });

        // test json
        {
            var requestBytes = requestJson.getBytes(StandardCharsets.UTF_8);
            System.out.println("--> %s".formatted(new String(requestBytes)));
            var responseBytes = processor.process(requestBytes);
            System.out.println("<-- %s".formatted(new String(responseBytes)));
            var responseAsParsedJson = objectMapper.readValue(responseBytes, new TypeReference<List<Object>>() {
            });
            assertEquals(expectedResponseAsParsedJson, responseAsParsedJson);
        }
    }

    public static void testBinary(String requestJson, String expectedResponseJson) throws IOException {
        var objectMapper = new ObjectMapper();
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var processor = new Server(json, TestUtility::handle).setOnError((e) -> e.printStackTrace());
        var expectedResponseAsParsedJson = objectMapper.readValue(expectedResponseJson,
                new TypeReference<List<Object>>() {
                });

        // test binary
        {
            Adapter adapter = (m, s) -> {
                return CompletableFuture.supplyAsync(() -> {
                    var requestBytes = s.serialize(m);
                    System.out.println("--> %s".formatted(new String(requestBytes)));
                    var responseBytes = processor.process(requestBytes);
                    System.out.println("<-- %s".formatted(new String(responseBytes)));
                    List<Object> response = s.deserialize(responseBytes);
                    return response;
                });
            };
            var client = new Client(adapter).setForceSendJsonDefault(false).setUseBinaryDefault(true);
            client.submit(new Request("_ping", Map.of())); // warmup
            var requestAsParsedJson = objectMapper.readValue(requestJson, new TypeReference<List<Object>>() {
            });

            if (expectedResponseJson.startsWith("[\"error.")) {
                var e = assertThrows(JApiError.class,
                        () -> client.submit(new Request(((String) requestAsParsedJson.get(0)).substring(9),
                                (Map<String, Object>) requestAsParsedJson.get(2)).addHeaders(
                                        (Map<String, Object>) requestAsParsedJson.get(1))));
                assertEquals(expectedResponseAsParsedJson.get(0), e.target);
                assertEquals(expectedResponseAsParsedJson.get(2), e.body);
            } else {
                var outputAsParsedJson = client.submit(new Request(((String) requestAsParsedJson.get(0)).substring(9),
                        (Map<String, Object>) requestAsParsedJson.get(2)).addHeaders(
                                (Map<String, Object>) requestAsParsedJson.get(1)));
                assertEquals(expectedResponseAsParsedJson.get(2), outputAsParsedJson);
            }
        }
    }

}
